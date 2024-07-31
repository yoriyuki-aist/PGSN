from __future__ import annotations
from typing import TypeAlias
from abc import ABC, abstractmethod
from attrs import field, frozen, evolve
from meta_info import MetaInfo
import helpers

Term: TypeAlias = "Term"
Named: TypeAlias = "Named"
Nameless: TypeAlias = "Nameless"


@frozen(kw_only=True)
class Term(ABC):
    # meta_info is always not empty
    meta_info: MetaInfo = field(default=MetaInfo(), eq=False)


@frozen(kw_only=True)
class Nameless(Term):

    @abstractmethod
    def eval_or_none(self) -> Nameless | None:
        pass

    def eval(self) -> Named:
        evaluated = helpers.default(self.eval_or_none(), self)
        return evaluated

    @abstractmethod
    def shift(self, num: int, cutoff: int) -> Nameless:
        pass

    @abstractmethod
    def subst_or_none(self, variable: int, term: Nameless) -> Nameless | None:
        pass

    def subst(self, variable:int, term: Nameless) -> Nameless:
        substituted_or_none = self.subst_or_none(variable, term)
        substituted = helpers.default(substituted_or_none,  self)
        return substituted


@frozen
class Variable(Nameless):
    num: int = field(validator=helpers.non_negative)

    def eval_or_none(self):
        return None

    def shift(self, d, cutoff):
        if self.num < cutoff:
            return self
        else:
            return evolve(self, num=self.num+d)

    def subst_or_none(self, num, term) -> Variable | None:
        if self.num == num:
            return term
        else:
            return None

    def recover_name_with_context(self, context, default_name='x'):
        if 0 <= self.num < len(context):
            return NamedVariable(meta_info=self.meta_info,
                                 name=context[self.num])
        else:
            name = helpers.default(self.meta_info.name_info, default_name)
            return NamedVariable(meta_info=self.meta_info,
                                 name=f"{name}_{self.num}")


@frozen
class Abs(Nameless):
    t: Nameless = field(validator=helpers.not_none)

    def eval_or_none(self):
        reduced = self.t.eval_or_none()
        if reduced is None:
            return None
        else:
            return evolve(self, t=reduced)

    def shift(self, d, c):
        return evolve(self, t=self.t.shift(d, c+1))

    def subst_or_none(self, var, term) -> Abs | None:
        term_shifted = term.shift(1, 0)
        substituted = self.t.subst_or_none(var, term_shifted)
        if substituted is None:
            return None
        else:
            return evolve(self, t=substituted)


@frozen
class App(Nameless):
    t1: Nameless = field(validator=helpers.not_none)
    t2: Nameless = field(validator=helpers.not_none)

    def eval_or_none(self):
        t1_eval = self.t1.eval_or_none()
        t2_eval = self.t2.eval_or_none()
        t1_prime = helpers.default(t1_eval, self.t1)
        t2_prime = helpers.default(t2_eval, self.t2)
        if isinstance(t1_prime, Abs):
            t_substituted = t1_prime.t.subst(0, t2_prime.shift(1, 0))
            return t_substituted.shift(-1, 0)
        elif isinstance(t1_prime, Builtin) and t1_prime.applicable(t2_prime):
            t = t1_prime.apply_arg(t2_prime)
            return t
        else:
            if t1_eval is None and t2_eval is None:
                return None
            else:
                return evolve(self, t1=t1_prime, t2=t2_prime)

    def shift(self, d, c):
        return evolve(self, t1=self.t1.shift(d, c), t2=self.t2.shift(d, c))

    def subst_or_none(self, var, term) -> App | None:
        t1_subst = self.t1.subst(var, term)
        t2_subst = self.t2.subst(var, term)
        if t1_subst is None and t2_subst is None:
            return None
        else:
            return evolve(self, t1=self.t1.subst(var, term), t2=self.t2.subst(var, term))


@frozen(kw_only=True)
class Named(Term):

    @classmethod
    def naming_context(cls, names: set[str]) -> list[str]:
        return sorted(list(names))

    @abstractmethod
    def free_variables(self) -> set[str]:
        pass

    @abstractmethod
    def remove_name_with_context(self, naming_context: list[str]) -> Nameless:
        pass

    def my_naming_context(self):
        return self.naming_context(self.free_variables())

    def remove_name(self) -> Nameless:
        return self.remove_name_with_context(self.my_naming_context())


@frozen(order=True)
class NamedVariable(Named):
    name: str = field(validator=helpers.not_none)
    meta_info : MetaInfo

    @classmethod
    def from_name(cls, name, debug_info=None):
        meta_info = MetaInfo(debug_info=debug_info, name_info=name)
        return cls(name=name, meta_info=meta_info)

    def free_variables(self):
        return {self.name}

    def remove_name_with_context(self, naming_context):
        meta_info = evolve(self.meta_info, name_info=self.name)
        num = naming_context.index(self.name)
        return Variable(num=num, meta_info=meta_info)


@frozen
class NamedAbs(Named):
    v: NamedVariable = field(validator=helpers.not_none)
    t: Named = field(validator=helpers.not_none)

    def free_variables(self):
        f_vars = self.t.free_variables()
        return f_vars - {self.v.name}

    def remove_name_with_context(self, context):
        meta_info = evolve(self.meta_info, name_info=self.v.name)
        new_context = [self.v.name] + context
        name_less_t = self.t.remove_name_with_context(new_context)
        return Abs(t=name_less_t, meta_info=meta_info)


@frozen
class NamedApp(Named):
    t1: Named = field(validator=helpers.not_none)
    t2: Named = field(validator=helpers.not_none)

    def free_variables(self):
        return self.t1.free_variables() | self.t2.free_variables()

    def remove_name_with_context(self, context):
        nameless_t1 = self.t1.remove_name_with_context(context)
        nameless_t2 = self.t2.remove_name_with_context(context)
        return App(meta_info=self.meta_info,
                   t1=nameless_t1,
                   t2=nameless_t2)


# Constants: any python data is okay
@frozen
class Constant(Nameless):
    name: str = field(validator=helpers.not_none)

    def eval_or_none(self):
        return None

    def shift(self, d, c):
        return self

    def subst_or_none(self, var, term):
        return None

    def recover_name_with_context(self, context, default_name='x'):
        return ConstantNamed(name=self.name, meta_info=self.meta_info)


@frozen
class ConstantNamed(Named):
    name: str = field(validator=helpers.not_none)

    def free_variables(self):
        return set()

    def remove_name_with_context(self, _):
        return Constant(name=self.name, meta_info=self.meta_info)


# Builtin functions.  Arity is always one.
@frozen
class Builtin(Nameless):
    name: str

    def eval_or_none(self) -> None:
        return None

    def shift(self, d, cutoff) -> Builtin:
        return self

    def subst_or_none(self, num, term) -> None:
        return None

    @abstractmethod
    def applicable(self, arg:Nameless) -> bool:
        pass

    @abstractmethod
    def _apply_arg(self, arg: Nameless) -> Nameless:
        pass

    def apply_arg(self, arg: Nameless) -> Nameless:
        assert self.applicable(arg)
        return self._apply_arg(arg)



