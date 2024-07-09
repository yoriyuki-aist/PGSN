from __future__ import annotations
from typing import TypeAlias
from abc import ABC, abstractmethod
from attrs import field, frozen, evolve, define
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
        return helpers.default(self.eval_or_none(), self)

    @abstractmethod
    def shift(self, num: int, cutoff: int) -> Nameless:
        pass

    @abstractmethod
    def subst_or_none(self, variable: int, term: Nameless) -> Nameless | None:
        pass

    def subst(self, variable:int, term: Nameless) -> Nameless:
        return helpers.default(self.subst_or_none(variable, term), self)

    @abstractmethod
    def recover_name_with_context(self, context: list[str], default_name) -> Named:
        pass

    def recover_name(self) -> Named:
        return self.recover_name_with_context([])


@frozen
class NamelessVariable(Nameless):
    __match_args__ = ('num',)
    num: int = field(validator=helpers.non_negative)

    def eval_or_none(self):
        return None

    def shift(self, d, cutoff):
        if self.num < cutoff:
            return self
        else:
            return evolve(self, num=self.num+d)

    def subst_or_none(self, num, term):
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

    def subst_or_none(self, var, term):
        term_shifted = term.shift(-1, 0)
        substituted = self.t.subst_or_none(var+1, term_shifted)
        if substituted is None:
            return None
        else:
            return evolve(self, t=substituted)

    def recover_name_with_context(self, context, default_name='x'):
        name = helpers.default(self.meta_info.name_info, default_name)
        new_context = [name] + context
        named_term = self.t.recover_name_with_context(context=new_context,
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
        t2_prime = helpers.default(t2_eval, self.t2)
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

    def subst_or_none(self, var, term):
        t1_subst = self.t1.subst(var, term)
        t2_subst = self.t2.subst(var, term)
        if t1_subst is None and t2_subst is None:
            return None
        else:
            return evolve(self, t1=self.t1.subst(var, term), t2=self.t2.subst(var, term))

    def recover_name_with_context(self, context, default_name='x'):
        named_t1 = self.t1.recover_name_with_context(context, default_name)
        named_t2 = self.t2.recover_name_with_context(context, default_name)
        return NamedApp(meta_info=self.meta_info, t1=named_t1, t2=named_t2)


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


# Arbitrary Python data
@frozen
class DataNameless(Nameless):
    value: any = field(validator=helpers.not_none)

    def eval_or_none(self):
        return None

    def shift(self, d, c):
        return self

    def subst_or_none(self, var, term):
        return None

    def recover_name_with_context(self, context, default_name='x'):
        return DataNamed(self.value)


@frozen
class DataNamed(Named):
    value: any = field(validator=helpers.not_none)

    def free_variables(self):
        return set()

    def remove_name_with_context(self, _):
        return DataNameless(self.value)


# List

@frozen
class ListNameless(Nameless):
    terms: list[Nameless] = field(validator=helpers.not_none)

    def eval_or_none(self):
        evaluated = [term.eval_or_none() for term in self.terms]
        if all(t is None for t in evaluated):
            return None
        else:
            return evaluated

    def shift(self, d, c):
        shifted = [t.shift(d, c) for t in self.terms]
        return evolve(self, terms=shifted)

    def subst_or_none(self, num, term):
        subst = [t.subst_or_none(num, term) for t in self.terms]
        if all(t is None for t in subst):
            return None
        else:
            return subst

    def recover_name_with_context(self, context, default):
        return ListNamed([t.recover_name_with_context(context, default) for t in self.terms])


@frozen
class ListNamed(Named):
    terms : list[Named] = field(default=[],
                                validator=helpers.not_none)

    def free_variables(self):
        return set().union(*{t.free_variables() for t in self.terms})

    def remove_name_with_context(self, context):
        return ListNameless([t.remove_name_with_context(context) for t in self.terms])


@frozen
class RecordNameless(Nameless):
    terms: dict[str, Nameless] = field(default={},
                                  validator=helpers.not_none)

    def eval_or_none(self):
        evaluated = {label: t.eval_or_none() for label, t in self.terms.items()}
        if all(t is None for t in evaluated.values()):
            return None
        else:
            return evaluated

    def shift(self, d, c):
        shifted = {label: t.shift(d, c) for label, t in self.terms.items()}
        return evolve(self, terms=shifted)

    def subst_or_none(self, num, term):
        subst = {label: t.subst_or_none(num, term) for label, t in self.terms.items()}
        if all(t is None for t in subst.values()):
            return None
        else:
            return subst

    def recover_name_with_context(self, context, default):
        return RecordNamed({label: t.recover_name_with_context(context, default) for label, t in self.terms.items()})


@frozen
class RecordNamed(Named):
    terms: dict[str, Named] = field(default={},
                               validator=helpers.not_none)

    def free_variables(self):
        return set().union(*{t.free_variables() for t in self.terms.values()})

    def remove_name_with_context(self, context):
        return RecordNameless({label: t.remove_name_with_context(context) for label, t in self.terms.items()})


