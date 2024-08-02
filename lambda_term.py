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
            return evolve(self, name=name)
        if num is not None and name is None and not self.name:
            assert self.num is not None and self.name is None
            return evolve(self, num=num)
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
            return evolve(self, num=self.num+d)

    def _subst_or_none(self, num, term) -> Nameless | None:
        if self.num == num:
            return term
        else:
            return None

    def _remove_name_with_context(self, context: list[str]) -> Term:
        meta_info = evolve(self.meta_info, name_info=self.name)
        num = context.index(self.name)
        return Variable.nameless_term(num=num, meta_info=self.meta_info)


@frozen
class Abs(Term):
    @classmethod
    def _nameless_term(cls, *kwarg):
        pass

    @classmethod
    def _named_term(cls, *kwarg):
        pass

    def evolve(self, *kwarg):
        pass

    def _named_validator(self, attribute, value):
        pass

    def _eval_or_none(self) -> Term | None:
        pass

    def _shift(self, num: int, cutoff: int) -> Term:
        pass

    def _subst_or_none(self, variable: int, term: Term) -> Term | None:
        pass

    def _free_variables(self) -> set[str]:
        pass

    def _remove_name_with_context(self, context: list[str]) -> Term:
        pass

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
        return NamedConstant(name=self.name, meta_info=self.meta_info)


@frozen
class NamedConstant(Named):
    name: str = field(validator=helpers.not_none)

    @classmethod
    def from_nameless(cls, const: Constant):
        return cls(name=const.name)

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


@frozen
class NamedBuiltin(Named):
    name: str = field(validator=helpers.not_none)

    @classmethod
    def from_nameless(cls, builtin: Builtin):
        cls(name=builtin.name)

    def free_variables(self):
        return set()

    def remove_name_with_context(self, _):
        return Builtin(name=self.name, meta_info=self.meta_info)



