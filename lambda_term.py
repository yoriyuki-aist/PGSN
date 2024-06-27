from __future__ import annotations
from typing import TypeAlias
from attrs import field, frozen, evolve, define
from meta_info import MetaInfo
import helpers

Term: TypeAlias = "Term"
Named: TypeAlias = "Named"
Nameless: TypeAlias = "Nameless"


@frozen(kw_only=True)
class Term:
    # meta_info is always not empty
    meta_info: MetaInfo = field(default=MetaInfo(), eq=False)


@frozen(kw_only=True)
class Nameless(Term):

    def eval_or_none(self) -> Nameless | None:
        pass

    def eval(self) -> Named:
        return helpers.default(self.eval_or_none(), self)

    def shift(self, num: int, cutoff: int) -> Nameless:
        pass

    def subst(self, variable: int, term: Nameless) -> Nameless:
        pass

    def recover_name_with_name_context(self, context: list[str], default_name) -> Named:
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

    def recover_name_with_name_context(self, context, default_name='x'):
        if 0 <= self.num < len(context):
            return NamedVariable(meta_info=self.meta_info,
                                 name=context[self.num])
        else:
            name = helpers.default(self.meta_info.name_info, default_name)
            return NamedVariable(meta_info=self.meta_info,
                                 name=f"{name}_{self.num}")


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
        term_shifted = term.shift(-1, 0)
        return evolve(self, t=self.t.subst(var+1, term_shifted))

    def recover_name_with_name_context(self, context, default_name='x'):
        name = helpers.default(self.meta_info.name_info, default_name)
        new_context = [name] + context
        named_term = self.t.recover_name_with_name_context(context=new_context,
                                                           default_name=default_name)
        named_variable = NamedVariable(name)
        return NamedAbs(meta_info=self.meta_info, v=named_variable, t=named_term)


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
        return evolve(self, t1=self.t1.shift(d, c), t2=self.t2.shift(d, c))

    def subst(self, var, term):
        return evolve(self, t1=self.t1.subst(var, term), t2=self.t2.subst(var, term))

    def recover_name_with_name_context(self, context, default_name='x'):
        named_t1 = self.t1.recover_name_with_name_context(context, default_name)
        named_t2 = self.t2.recover_name_with_name_context(context, default_name)
        return NamedApp(meta_info=self.meta_info, t1=named_t1, t2=named_t2)


    # @frozen
    # class DataInNameless(Nameless):
    #     val: any = field(validator=helpers.not_none)
    #
    #     def eval_or_none(self):
    #         return self
    #
    #     def shift(self, d, c):
    #         return self
    #
    #     def recover_name_with_name_context(self, context, default_name='x'):
    #         return DataInNamed(self.val)


@frozen(kw_only=True)
class Named(Term):

    @classmethod
    def naming_context(cls, names: set[str]) -> list[str]:
        return sorted(list(names))

    def free_variables(self) -> set[str]:
        pass

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
        return {self.name}

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
        return f_vars - {self.v.name}

    def remove_name_with_context(self, context):
        meta_info = evolve(self.meta_info, name_info=self.v.name)
        new_context = [self.v.name] + context
        name_less_t = self.t.remove_name_with_context(new_context)
        return NamelessAbs(t=name_less_t, meta_info=meta_info)


@frozen
class NamedApp(Named):
    t1: Named = field(validator=helpers.not_none)
    t2: Named = field(validator=helpers.not_none)

    def free_variables(self):
        return self.t1.free_variables() | self.t2.free_variables()

    def remove_name_with_context(self, context):
        nameless_t1 = self.t1.remove_name_with_context(context)
        nameless_t2 = self.t2.remove_name_with_context(context)
        return NamelessApp(meta_info=self.meta_info,
                           t1=nameless_t1,
                           t2=nameless_t2)


    # @frozen
    # class DataInNamed(Named):
    #     val: any = field(validator=helpers.not_none)
    #
    #     def free_variables(self):
    #
