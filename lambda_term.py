from __future__ import annotations
from typing import TypeAlias
from abc import ABC, abstractmethod
from attrs import field, frozen, evolve
from meta_info import MetaInfo
import meta_info as meta
import helpers

Term: TypeAlias = "Term"


def is_named(instance, attribute, value):
    assert value.is_named


def is_nameless(instance, attribute, value):
    assert not value.is_named


def naming_context(names: set[str]) -> list[str]:
    return sorted(list(names))


@frozen(kw_only=True)
class Term(ABC):
    # meta_info is always not empty
    meta_info: MetaInfo = field(default=MetaInfo(), eq=False)
    is_named: bool = field(validator=helpers.not_none)

    @classmethod
    @abstractmethod
    def nameless(cls, meta_info=meta.empty, *kwarg) -> Term:
        pass

    @classmethod
    @abstractmethod
    def named(cls, meta_info=meta.empty, *kwarg) -> Term:
        pass

    @abstractmethod
    def evolve(self, *kwarg):
        pass

    # Only application becomes closure, otherwise None
    @abstractmethod
    def _eval_or_none(self):
        pass

    def eval_or_none(self):
        assert not self.is_named
        evaluated = self._eval_or_none()
        assert (evaluated is None) or (not evaluated.is_named)
        return evaluated
    # If None is returned, the reduction is terminated.
    def eval(self) -> Term:
        evaluated = helpers.default(self.eval_or_none(), self)
        assert(not evaluated.is_named)
        return evaluated

    @abstractmethod
    def _shift(self, num: int, cutoff: int) -> Term:
        pass

    def shift(self, num: int, cutoff: int) -> Term:
        assert not self.is_named
        shifted = self._shift(num, cutoff)
        assert not shifted.is_named
        return shifted

    @abstractmethod
    def _subst_or_none(self, variable: int, term: Term) -> Term | None:
        pass

    def subst_or_none(self, variable: int, term: Term) -> Term | None:
        assert not self.is_named
        assert not term.is_named
        substituted = self._subst_or_none(variable, term)
        assert not substituted.is_named
        return substituted

    def subst(self, variable:int, term: Term) -> Term:
        substituted_or_none = self.subst_or_none(variable, term)
        substituted = helpers.default(substituted_or_none,  self)
        return substituted

    @abstractmethod
    def _free_variables(self) -> set[str]:
        pass

    def free_variables(self) -> set[str]:
        assert self.is_named
        return self._free_variables()

    @abstractmethod
    def _remove_name_with_context(self, context: list[str]) -> Term:
        pass

    def remove_name_with_context(self, context: list[str]) -> Term:
        assert self.is_named
        nameless = self._remove_name_with_context(context)
        assert not nameless.is_named
        return nameless

    def my_naming_context(self) -> list[str]:
        assert self.is_named
        return naming_context(self.free_variables())

    def remove_name(self) -> Term:
        assert self.is_named
        return self.remove_name_with_context(self.my_naming_context())

    def __call__(self, arg: Term) -> Term:
        assert self.is_named == arg.is_named
        return App(self, arg, is_named=self.is_named)


@frozen
class Variable(Term):
    num: int | None = field()
    name: str | None = field()
    is_named: bool = field()

    @classmethod
    def nameless(cls, num=0, meta_info=meta.empty) -> Variable:
        return Variable(num=num, name=None, meta_info=meta_info, is_named=False)

    @classmethod
    def named(cls, name=name, meta_info=meta.empty) -> Variable:
        return Variable(num=None, name=name, is_named=True, meta_info=meta_info)

    @classmethod
    def from_name(cls, name:str):
        return cls.named(name=name)

    def evolve(self, num: int = None, name: str = None):
        if num is None and name is not None:
            return evolve(self, num=None, name=name, is_named=True)
        if num is not None and name is None:
            return evolve(self, num=num, name=None, is_named=False)
        else:
            assert False

    def _free_variables(self) -> set[str]:
        return {self.name}

    def _eval_or_none(self):
        return None

    def _shift(self, d, cutoff):
        if self.num < cutoff:
            return self
        else:
            return self.evolve(num=self.num+d)

    def _subst_or_none(self, num, term) -> Term | None:
        if self.num == num:
            return term
        else:
            return None

    def _remove_name_with_context(self, context: list[str]) -> Term:
        num = context.index(self.name)
        return self.evolve(num=num)


@frozen
class Abs(Term):
    v: Variable | None = field()
    t: Term = field(validator=helpers.not_none)

    @classmethod
    def nameless(cls, t=t, meta_info=meta.empty):
        assert not t.is_named
        return Abs(is_named=False, v=None, t=t, meta_info=meta_info)

    @classmethod
    def named(cls, v=v, t=t):
        assert v is not None and v.is_named and t.is_named
        return Abs(is_named=True, v=v, t=t, meta_info=meta.empty)

    def __attr_post_init__(self):
        assert self.v.is_named == self.t.is_named

    def evolve(self, t: Term, v: Variable | None = None):
        if v is None and not t.is_named:
            return evolve(self, v=v, t=t, is_named=False)
        elif v is not None and v.is_named and t.is_named:
            return evolve(self, v=v, t=t, is_named=True)
        else:
            assert False

    def _eval_or_none(self) -> Term | None:
        t_evaluated = self.t.eval_or_none()
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
        return self.evolve(t=name_less_t, v=None)


@frozen
class App(Term):
    t1: Term = field(validator=helpers.not_none)
    t2: Term = field(validator=helpers.not_none)

    @classmethod
    def nameless(cls, t1: Term = t1, t2: Term = t2, meta_info: MetaInfo = meta.empty):
        assert not t1.is_named and not t2.is_named
        return App(is_named=False, t1=t1, t2=t2, meta_info=meta_info)

    @classmethod
    def named(cls, t1: Term = t1, t2: Term = t2):
        assert t1.is_named and t2.is_named
        return App(is_named=True, t1=t1, t2=t2)

    @classmethod
    def term(cls, t1: Term, t2: Term):
        if t1.is_named and t2.is_named:
            return cls.named(t1, t2)
        elif not t1.is_named and not t2.is_named:
            return cls.nameless(t1, t2)
        else:
            assert False

    def __attr_post_init__(self):
        assert self.t1.is_named == self.t2.is_named

    def evolve(self, t1: Term, t2:Term):
        if t1.is_named and t2.is_named:
            return evolve(self, t1=t1, t2=t2, is_named=True)
        elif not t1.is_named and not t2.is_named:
            return evolve(self, t1=t1, t2=t2, is_named=False)
        else:
            assert False

    def to_closure(self) -> Closure:
        if isinstance(self.t1, App):
            return self.t1.to_closure().stack(self.t2)
        else:
            return Closure(head=self.t1, args=(self.t2,))

    def _eval_or_none(self):
        if isinstance(self.t1, App):
            c = self.t1.to_closure().stack(self.t2)
        else:
            c = Closure(head=self.t1, args=(self.t2,))
        c_reduced = c.reduce_or_none()
        if c_reduced is None:
            return None
        else:
            return c_reduced.to_term()

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
        return self.evolve(t1=nameless_t1, t2=nameless_t2)


# leftmost, outermost reduction
@frozen
class Closure:
    head: Term = field(validator=helpers.not_none)
    args: tuple[Term] = field(default=(), validator=helpers.not_none)

    @classmethod
    def build(cls, head, args):
        if isinstance(head, App):
            return cls.build(head=head.t1, args=(head.t2,) + args)

    def evolve(self, head=None, args=None):
        if head is None:
            head = self.head
        if args is None:
            args = self.args
        return Closure(head=head, args=args)

    def to_term(self) -> Term:
        term = self.head
        for arg in self.args:
            term = App.nameless(term, arg)
        return term

    def stack(self, arg: Term):
        return self.evolve(args=self.args + (arg, ))

    # If None is returned, the reduction is terminated.
    def reduce_or_none(self) -> Closure | None:
        head_reduced = self.head.eval_or_none()
        if head_reduced is not None:
            return evolve(self, head=head_reduced)
        if len(self.args) == 0:
            return None
        if isinstance(self.head, Abs):
            head_substituted = self.head.t.subst(0, self.args[0].shift(1, 0))
            return self.evolve(head=head_substituted, args=self.args[1:])
        if isinstance(self.head, Builtin):
            if self.head.applicable(self.args):
                reduced = self.head.apply_args(self.args)
                return self.evolve(head=reduced, args=tuple())
        else:
            for i in range(len(self.args)):
                arg_reduced = self.args[i].eval_or_none()
                if arg_reduced is not None:
                    new_args = self.args[0:i-1] + (arg_reduced,) + self.args[i+1:]
                    return self.evolve(args=new_args)
            return None


class Builtin(Term):

    @abstractmethod
    def _applicable(self, args: tuple[Term]) -> bool:
        pass

    def applicable(self, args: tuple[Term]) -> bool:
        assert(not self.is_named and all(not arg.is_named for arg in args))
        return self._applicable(args)

    @abstractmethod
    def _apply_args(self, args: tuple[Term]) -> Term:
        pass

    def apply_args(self, args: tuple[Term]) -> Term:
        assert self.applicable(args)
        return self._apply_args(args)


@frozen
class Constant(Builtin):
    name: str = field(validator=helpers.not_none)

    @classmethod
    def named(cls, meta_info=meta.empty, name=name):
        return Constant(name=name, is_named=True)

    @classmethod
    def nameless(cls, meta_info=meta.empty, name=name):
        return Constant(name=name, is_named=False)

    def evolve(self, name: str, is_named: bool):
        return evolve(self, name=name)

    def _eval_or_none(self) -> Term | None:
        return None

    def _shift(self, num: int, cutoff: int) -> Term:
        return self

    def _subst_or_none(self, variable: int, term: Term) -> Term | None:
        return None

    def _free_variables(self) -> set[str]:
        return set()

    def _remove_name_with_context(self, context: list[str]) -> Term:
        return evolve(self, is_named=False)

    def _applicable(self, args):
        return False

    def _apply_args(self, args):
        assert False


# Builtin functions.  Arity is always one.
@frozen
class BuiltinFunction(Builtin):
    name: str = field(validator=helpers.not_none)

    @classmethod
    def nameless(cls, meta_info=meta.empty, name=name):
        return cls(name=name, is_named=False, meta_info=meta_info)

    @classmethod
    def named(cls, meta_info=meta.empty, name=name):
        return cls(name=name, is_named=True)

    def evolve(self, name=name):
        return evolve(self, name=name)

    def _eval_or_none(self) -> None:
        return None

    def _shift(self, d, cutoff) -> BuiltinFunction:
        return self

    def _subst_or_none(self, num, term) -> None:
        return None

    @abstractmethod
    def _applicable(self, arg: Term) -> bool:
        pass

    @abstractmethod
    def _apply_args(self, arg: Term) -> Term:
        pass

    def _free_variables(self) -> set[str]:
        return set()

    def _remove_name_with_context(self, context: list[str]) -> Term:
        return evolve(self, is_named=False)



