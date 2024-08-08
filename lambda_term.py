from __future__ import annotations
from typing import TypeAlias
from abc import ABC, abstractmethod
from attrs import field, frozen, evolve
from meta_info import MetaInfo
import meta_info as meta
import helpers

Term: TypeAlias = "Term"
Named: TypeAlias = "Named"
Nameless: TypeAlias = "Nameless"


def is_named(instance, attribute, value):
    assert value.named


def is_nameless(instance, attribute, value):
    assert not value.named


def naming_context(names: set[str]) -> list[str]:
    return sorted(list(names))


@frozen(kw_only=True)
class Term(ABC):
    # meta_info is always not empty
    meta_info: MetaInfo = field(default=MetaInfo(), eq=False)
    named: bool = field()

    @classmethod
    @abstractmethod
    def _nameless_term(cls, *kwarg):
        pass

    @classmethod
    def nameless_term(cls, *kwarg):
        obj = cls._nameless_term(*kwarg)
        obj.named = False
        return obj

    @classmethod
    @abstractmethod
    def _named_term(cls, *kwarg):
        pass

    @classmethod
    def named_term(cls, *kwarg):
        obj = cls._named_term(*kwarg)
        obj.named = True
        return obj

    @abstractmethod
    def evolve(self, *kwarg):
        pass

    @named.validator
    @abstractmethod
    def _named_validator(self, attribute, value):
        pass

    @abstractmethod
    def _eval_or_none(self) -> Term | None:
        pass

    def eval_or_none(self) -> Term | None:
        assert not self.named
        evaluated = self._eval_or_none()
        assert (evaluated is None) or (not evaluated.named)
        return evaluated

    def eval(self) -> Term:
        evaluated = helpers.default(self.eval_or_none(), self)
        return evaluated

    @abstractmethod
    def _shift(self, num: int, cutoff: int) -> Term:
        pass

    def shift(self, num: int, cutoff: int) -> Term:
        assert not self.named
        shifted = self._shift(num, cutoff)
        assert not shifted.named
        return shifted

    @abstractmethod
    def _subst_or_none(self, variable: int, term: Term) -> Term | None:
        pass

    def subst_or_none(self, variable: int, term: Term) -> Term | None:
        assert not self.named
        assert not term.named
        substituted = self._subst_or_none(variable, term)
        assert not substituted.named
        return substituted

    def subst(self, variable:int, term: Term) -> Term:
        substituted_or_none = self.subst_or_none(variable, term)
        substituted = helpers.default(substituted_or_none,  self)
        return substituted

    @abstractmethod
    def _free_variables(self) -> set[str]:
        pass

    def free_variables(self) -> set[str]:
        assert self.named
        return self.free_variables()

    @abstractmethod
    def _remove_name_with_context(self, context: list[str]) -> Term:
        pass

    def remove_name_with_context(self, context: list[str]) -> Term:
        assert self.named
        nameless = self._remove_name_with_context(context)
        assert not nameless.named
        return nameless

    def my_naming_context(self) -> list[str]:
        assert self.named
        return naming_context(self.free_variables())

    def remove_name(self) -> Term:
        assert self.named
        return self.remove_name_with_context(self.my_naming_context())


@frozen
class Variable(Term):
    num: int | None = field()
    name: str | None = field()
    named: bool = field()

    @classmethod
    def _nameless_term(cls, num=None, meta_info=meta.empty):
        assert num is not None
        return Variable(num=num, name=None, meta_info=meta_info, named=False)

    @classmethod
    def _named_term(cls, name=None, meta_info=meta.empty):
        assert name is not None
        return Variable(num=None, name=name, named=False, meta_info=meta_info)

    def evolve(self, num: int = None, name: str = None):
        if num is None and name is not None and self.named:
            assert self.num is None and self.name is not None
            return evolve(self, name=name, named=True)
        if num is not None and name is None and not self.name:
            assert self.num is not None and self.name is None
            return evolve(self, num=num, named=False)
        else:
            assert False

    def _named_validator(self, attribute, value):
        if value:
            assert self.num is None and self.name is not None
        else:
            assert self.num is not None and self.name is None

    def _free_variables(self) -> set[str]:
        return {self.name}

    def _eval_or_none(self):
        return None

    def _shift(self, d, cutoff):
        if self.num < cutoff:
            return self
        else:
            return self.evolve(num=self.num+d)

    def _subst_or_none(self, num, term) -> Nameless | None:
        if self.num == num:
            return term
        else:
            return None

    def _remove_name_with_context(self, context: list[str]) -> Term:
        num = context.index(self.name)
        return self.evolve(num=num)


@frozen
class Abs(Term):
    v: Variable | None = field(validator=helpers.not_none)
    t: Term = field(validator=helpers.not_none)

    def _named_validator(self, attribute, value):
        if value:
            assert self.v is not None and self.v.named and self.t.named
        else:
            assert self.v is None and not self.named

    @classmethod
    def _nameless_term(cls, t, meta_info=meta.empty):
        assert t.named is False
        return Abs(named=False, v=None, t=t, meta_info=meta_info)

    @classmethod
    def _named_term(cls, v, t):
        assert v is not None and v.named and t.named
        return Abs(named=True, v=v, t=t, meta_info=meta.empty)

    def evolve(self, t: Term, v: Variable | None = None):
        if v is None and not t.named:
            return evolve(self, v=v, t=t, named=False)
        elif v is not None and v.named and t.named:
            return evolve(self, v=v, t=t, named=True)
        else:
            assert False

    def _eval_or_none(self) -> Term | None:
        assert not self.named
        t_evaluated = self.t.eval()
        return None if t_evaluated is None else self.evolve(t=t_evaluated)

    def _shift(self, num: int, cutoff: int) -> Term:
        return self.evolve(t=self.t.shift(num, cutoff + 1))

    def _subst_or_none(self, var: int, term: Term) -> Term | None:
        term_shifted = term.shift(1, 0)
        substituted = self.t.subst_or_none(var, term_shifted)
        if substituted is None:
            return None
        else:
            return self.evolve(t=substituted)

    def _free_variables(self) -> set[str]:
        f_vars = self.t.free_variables()
        return f_vars - {self.v.name}

    def _remove_name_with_context(self, context: list[str]) -> Term:
        new_context = [self.v.name] + context
        name_less_t = self.t.remove_name_with_context(new_context)
        return self.evolve(t=name_less_t)


@frozen
class App(Term):
    t1: Term = field(validator=helpers.not_none)
    t2: Term = field(validator=helpers.not_none)

    @classmethod
    def _nameless_term(cls, t1: Term, t2: Term):
        assert not t1.named and not t2.named
        return App(named=False, t1=t1, t2=t2)

    @classmethod
    def _named_term(cls, t1: Term, t2: Term):
        assert t1.named and t2.named
        return App(named=True, t1=t1, t2=t2)

    @classmethod
    def term(cls, t1: Term, t2: Term):
        if t1.named and t2.named:
            return cls.named_term(t1, t2)
        elif not t1.named and not t2.named:
            return cls.nameless_term(t1, t2)
        else:
            assert False

    def _named_validator(self, attribute, value):
        if self.t1.named and self.t2.named:
            assert self.named
        elif not self.t1.named and not self.t2.named:
            assert not self.named
        else:
            assert False

    def evolve(self, t1: Term, t2:Term):
        if t1.named and t2.named:
            return evolve(self, t1=t1, t2=t2, named=True)
        elif not t1.named and not t2.named:
            return evolve(self, t1=t1, t2=t2, named=False)
        else:
            assert False

    def _eval_or_none(self) -> Term | None:
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
                return self.evolve(t1=t1_prime, t2=t2_prime)

    def _shift(self, num: int, cutoff: int) -> Term:
        return self.evolve(t1=self.t1.shift(num, cutoff), t2=self.t2.shift(num, cutoff))

    def _subst_or_none(self, var: int, term: Term) -> Term | None:
        t1_subst = self.t1.subst(var, term)
        t2_subst = self.t2.subst(var, term)
        if t1_subst is None and t2_subst is None:
            return None
        else:
            return self.evolve(t1=self.t1.subst(var, term), t2=self.t2.subst(var, term))

    def _free_variables(self) -> set[str]:
        return self.t1.free_variables() | self.t2.free_variables()

    def _remove_name_with_context(self, context: list[str]) -> Term:
        nameless_t1 = self.t1.remove_name_with_context(context)
        nameless_t2 = self.t2.remove_name_with_context(context)
        return self.evolve(t1=self.t1, t2=self.t2)


# Constants: any python data is okay
@frozen
class Constant(Term):
    name: str = field(validator=helpers.not_none)

    @classmethod
    def _nameless_term(cls, name=name):
        return Constant(name=name, named=False)

    @classmethod
    def _named_term(cls, name=name):
        return Constant(name=name, named=True)

    def evolve(self, name: str, named: bool):
        return evolve(self, name=name)

    def _named_validator(self, attribute, value):
        assert True

    def _eval_or_none(self) -> Term | None:
        return None

    def _shift(self, num: int, cutoff: int) -> Term:
        return self

    def _subst_or_none(self, variable: int, term: Term) -> Term | None:
        return None

    def _free_variables(self) -> set[str]:
        return set()

    def _remove_name_with_context(self, context: list[str]) -> Term:
        return evolve(self, named=False)


# Builtin functions.  Arity is always one.
@frozen
class Builtin(Term):
    name: str

    @classmethod
    def _nameless_term(cls, name):
        return Builtin(name=name, named=False)

    @classmethod
    def _named_term(cls, name):
        return Builtin(name=name, named=True)

    def eval_or_none(self) -> None:
        return None

    def shift(self, d, cutoff) -> Builtin:
        return self

    def subst_or_none(self, num, term) -> None:
        return None

    @abstractmethod
    def _applicable(self, arg: Term) -> bool:
        pass

    def applicable(self, arg: Term) -> bool:
        if self.named or arg.named:
            return False
        else:
            return self._applicable(arg)

    @abstractmethod
    def _apply_arg(self, arg: Term) -> Term:
        pass

    def apply_arg(self, arg: Term) -> Term:
        assert self.applicable(arg)
        return self._apply_arg(arg)

    def __call__(self, arg: Term) -> Term:
        if self.applicable(arg):
            return self.apply_arg(arg)
        else:
            return App.term(self, arg)





