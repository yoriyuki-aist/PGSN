from __future__ import annotations
import abc
from typing import TypeAlias
from attrs import field, frozen, evolve, define
from meta_info import MetaInfo
import helpers

Named: TypeAlias = "Named"
Nameless: TypeAlias = "Nameless"


@frozen(kw_only=True)
class Nameless(abc.ABC):
    meta_info: MetaInfo = MetaInfo.empty()

    @abc.abstractmethod
    def eval_or_none(self) -> Nameless | None:
        pass

    def eval(self) -> Named:
        return helpers.default(self.eval_or_none(), self)

    @abc.abstractmethod
    def shift(self, num: int, cutoff: int) -> Nameless:
        pass

    @abc.abstractmethod
    def subst(self, variable: int, term: Nameless) -> Nameless:
        pass

    @abc.abstractmethod
    def recover_name_with_name_context(self, context: list[str]) -> Named:
        pass

    def recover_name(self) -> Named:
        return self.recover_name_with_name_context([])


@frozen
class NamelessVariable(Nameless):
    __match_args__ = ('num',)
    num: int = field(validator=helpers.non_negative)

    def eval_or_none(self):
        return self

    def shift(self, d, cutoff):
        if self.num < cutoff:
            return self
        else:
            return evolve(self, num=self.num+d)

    def subst(self, num, term):
        if self.num == num:
            return term
        else:
            return self


@frozen
class NamelessAbs(Nameless):
    t: Nameless = field(validator=helpers.not_none)

    def eval_or_none(self):
        reduced = self.t.eval_or_none()
        if reduced is None:
            return None
        else:
            return evolve(self, t=reduced)

    def shift(self, d, c):
        return evolve(self, t=self.t.shift(d, c+1))

    def subst(self, var, term):
        return evolve(self, t=self.t.subst(var, term))


@frozen
class NamelessApp(Nameless):
    t1: Nameless = field(validator=helpers.not_none)
    t2: Nameless = field(validator=helpers.not_none)

    def eval_or_none(self):
        t1_eval = self.t1.eval_or_none()
        t2_eval = self.t2.eval_or_none()
        t1_prime = helpers.default(t1_eval, self.t1)
        t2_prime = helpers.default(t2_eval, self.t1)
        if isinstance(t1_prime, NamelessAbs):
            t2_shifted = self.t2.shift(1, 0)
            t_substituted = self.t1.subst(0, t2_shifted)
            return t_substituted.shift(-1, 0)
        else:
            if t1_eval is None and t2_eval is None:
                return None
            return evolve(self, t1=t1_prime, t2=t2_prime)

    def shift(self, d, c):
        return NamelessApp(t1=self.t1.shift(d, c), t2=self.t2.shift(d, c))

    def subst(self, var, term):
        return evolve(self, t1=self.t1.subst(var, term), t2=self.t2.subst(var, term))


@frozen(kw_only=True)
class Named(abc.ABC):
    meta_info: MetaInfo = MetaInfo.empty()

    @classmethod
    def naming_context(cls, vars: set[NamedVariable]) -> list[str]:
        names = set(map(lambda v: v.name, vars))
        return sorted(list(names))

    @abc.abstractmethod
    def free_variables(self) -> set[NamedVariable]:
        pass

    @abc.abstractmethod
    def remove_name_with_context(self, naming_context: list[str]) -> Nameless:
        pass

    def my_naming_context(self):
        return self.naming_context(self.free_variables())

    def remove_name(self) -> Nameless:
        return self.remove_name_with_context(self.my_naming_context())



@frozen(order=True)
class NamedVariable(Named):
    name: str = field(validator=helpers.not_none)

    def free_variables(self):
        return {self}

    def remove_name_with_context(self, naming_context):
        meta_info = evolve(self.meta_info, name_info=self.name)
        num = naming_context.index(self.name)
        return NamelessVariable(num=num, meta_info=meta_info)



@frozen
class NamedAbs(Named):
    v: NamedVariable = field(validator=helpers.not_none)
    t: Named = field(validator=helpers.not_none)

    def free_variables(self):
        f_vars = self.t.free_variables()
        return f_vars - {self.v}

    def remove_name_with_context(self, context):
        meta_info = evolve(self.meta_info, name_info=self.v.name)
        new_context = [self.v.name] + context
        name_less_t = self.t.remove_name_with_context(new_context)
        return NamelessAbs(t=name_less_t, meta_info=meta_info)


@frozen
class App(Named):
    t1: Named = field(validator=helpers.not_none)
    t2: Named = field(validator=helpers.not_none)

    def free_variables(self):
        return self.t1.free_variables() + self.t2.free_variables()

    def remove_name_with_context(self, context):
        nameless_t1 = self.t1.remove_name_with_context(context)
        nameless_t2 = self.t2.remove_name_with_context(context)
        return NamelessApp(meta_info=self.meta_info,
                                   t1=nameless_t1,
                                   t2=nameless_t2)

