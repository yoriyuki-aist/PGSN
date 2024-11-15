from __future__ import annotations
from typing import TypeAlias, Generic
from abc import ABC, abstractmethod
from attrs import field, frozen, evolve
from typing import TypeVar
from meta_info import MetaInfo
import meta_info as meta
import helpers

Term: TypeAlias = "Term"
T = TypeVar('T')


def is_named(instance, attribute, value):
    assert value.is_named


def is_nameless(instance, attribute, value):
    assert not value.is_named


def naming_context(names: set[str]) -> list[str]:
    return sorted(list(names))


class LambdaInterpreterError(Exception):
    pass


Castable: TypeAlias = "Term | int | str | bool | list | dict | None"


def cast(x: Castable, is_named: bool) -> Term:
    match x:
        case Term():
            return x
        case int():
            return Integer.build(is_named=is_named, value=x)
        case str():
            return String.build(is_named=is_named, value=x)
        case bool():
            return Boolean.build(is_named=is_named, value=x)
        case list():
            y = [cast(z, is_named=is_named) for z in x]
            return List.build(is_named=is_named, terms=y)
        case dict():
            y = {k: cast(z, is_named=is_named) for k, z in x.items()}
            return Record.build(is_named=is_named, attributes=y)
        case _: assert False


@frozen(kw_only=True)
class Term(ABC):
    # meta_info is always not empty
    meta_info: MetaInfo = field(default=meta.empty, eq=False)
    is_named: bool = field(validator=helpers.not_none)

    @classmethod
    def build(cls, is_named: bool, **kwarg) -> Term:
        return cls(is_named=is_named, **kwarg)

    @classmethod
    def nameless(cls, **kwarg) -> Term:
        return cls.build(is_named=False, **kwarg)

    @classmethod
    def named(cls, **kwarg) -> Term:
        return cls.build(is_named=True, **kwarg)

    def evolve(self, **kwarg):
        return evolve(self, **kwarg)

    # Only application becomes closure, otherwise None
    @abstractmethod
    def _eval_or_none(self):
        pass

    # If None is returned, the reduction is terminated.
    def eval_or_none(self):
        if self.is_named:
            t = self.remove_name()
        else:
            t = self
        evaluated = t._eval_or_none()
        assert (evaluated is None) or (not evaluated.is_named)
        return evaluated

    def eval(self) -> Term:
        t = self if not self.is_named else self.remove_name()
        evaluated = helpers.default(t.eval_or_none(), t)
        assert(not evaluated.is_named)
        return evaluated

    # FIXME: Use contexts in intermediate steps, not terms
    def fully_eval(self, step=1000) -> Term:
        t = self if not self.is_named else self.remove_name()
        for _ in range(step):
            t_reduced = t.eval_or_none()
            assert t_reduced is None or t_reduced != t  # should progress
            if t_reduced is None:
                return t
            t = t_reduced
        raise LambdaInterpreterError('Reduction did not terminate', t)

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
        assert substituted is None or not substituted.is_named
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

    def __call__(self, *args: Castable, **kwargs: Castable) -> Term:
        arg_terms = list(map(lambda x: cast(x, is_named=self.is_named), args))
        kwarg = Record.build(is_named=self.is_named,
                             attributes={k: cast(v, is_named=self.is_named) for k, v in kwargs.items()})
        t = self
        for arg in arg_terms:
            t = App.build(t1=t, t2=arg, is_named=self.is_named)
        if kwargs == {}:
            return t
        return App.build(t1=t, t2=kwarg, is_named=self.is_named)


@frozen
class Variable(Term):
    num: int | None = field(default=None)
    name: str | None = field(default=None)

    @num.validator
    def _check_num(self, _, v):
        assert self.is_named or v is not None

    @name.validator
    def _check_name(self, _, v):
        assert not self.is_named or v is not None

    @classmethod
    def from_name(cls, name:str):
        return cls.named(name=name)

    def evolve(self, num: int | None = None, name: str | None = None):
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

    @v.validator
    def _check_v(self, attribute, value):
        assert self.is_named or value is None
        assert not self.is_named or value.is_named and isinstance(value, Variable)

    @t.validator
    def _check_t(self, _, value):
        assert value.is_named == self.is_named

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
        substituted = self.t.subst_or_none(var + 1, term_shifted)
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

    @t1.validator
    def _check_t1(self, _, v):
        assert v.is_named == self.is_named

    @t1.validator
    def _check_t2(self, _, v):
        assert v.is_named == self.is_named

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

    def evolve(self, t1: Term | None = None, t2: Term | None = None):
        if t1 is None:
            t1 = self.t1
        if t2 is None:
            t2 = self.t2
        if t1.is_named and t2.is_named:
            return evolve(self, t1=t1, t2=t2, is_named=True)
        elif not t1.is_named and not t2.is_named:
            return evolve(self, t1=t1, t2=t2, is_named=False)
        else:
            assert False

    def to_context(self) -> Context:
        if isinstance(self.t1, App):
            return self.t1.to_context().stack(self.t2)
        else:
            return Context.build(head=self.t1, args=(self.t2,))

    def _eval_or_none(self):
        if isinstance(self.t1, App):
            c = self.t1.to_context().stack(self.t2)
        else:
            c = Context.build(head=self.t1, args=(self.t2,))
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
        return self.evolve(t1=t1_subst, t2=t2_subst)

    def _free_variables(self) -> set[str]:
        return self.t1.free_variables() | self.t2.free_variables()

    def _remove_name_with_context(self, context: list[str]) -> Term:
        nameless_t1 = self.t1.remove_name_with_context(context)
        nameless_t2 = self.t2.remove_name_with_context(context)
        return self.evolve(t1=nameless_t1, t2=nameless_t2)


# leftmost, outermost reduction


class Builtin(Term):
    # hack.  the default is an invalid value
    arity: int = field(validator=[helpers.not_none, helpers.non_negative])
    name: str | None = field()

    @abstractmethod
    def _applicable_args(self, args: tuple[Term, ...]) -> bool:
        pass

    def applicable_args(self, args: tuple[Term, ...]) -> bool:
        assert (not self.is_named and all(not arg.is_named for arg in args))
        return len(args) >= self.arity and self._applicable_args(args)

    @abstractmethod
    def _apply_args(self, args: tuple[Term, ...]) -> Term:
        pass

    def apply_args(self, args: tuple[Term, ...]) -> tuple[Term, tuple[Term, ...]]:
        assert self.applicable_args(args)
        reduced = self._apply_args(args)
        assert not reduced.is_named
        return reduced, args[self.arity:]

    def _remove_name_with_context(self, context: list[str]) -> Term:
        return evolve(self, is_named=False)


@frozen
class Constant(Builtin):
    name: str = field(validator=helpers.not_none)
    arity = 0

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

    def _applicable_args(self, _):
        return False

    def _apply_args(self, _):
        assert False


# Builtin functions.  Arity is always one.
@frozen
class BuiltinFunction(Builtin, ABC):

    def _eval_or_none(self) -> None:
        return None

    def _shift(self, d, cutoff) -> BuiltinFunction:
        return self

    def _subst_or_none(self, num, term) -> None:
        return None

    def _free_variables(self) -> set[str]:
        return set()

    def _remove_name_with_context(self, context: list[str]) -> Term:
        return evolve(self, is_named=False)


@frozen
class Unary(BuiltinFunction, ABC):
    arity = 1

    @abstractmethod
    def _applicable(self, arg: Term):
        pass

    @abstractmethod
    def _apply_arg(self, arg: Term):
        pass

    def _applicable_args(self, args: tuple[Term, ...]):
        return len(args) >= 1 and self._applicable(args[0])

    def _apply_args(self, args: tuple[Term, ...]):
        return self._apply_arg(args[0])


# Evaluation Context
@frozen
class Context:
    head: Term = field(validator=helpers.not_none)
    args: tuple[Term,...] = field(default=(), validator=helpers.not_none)

    @classmethod
    def build(cls, head, args):
        if isinstance(head, App):
            return cls.build(head=head.t1, args=(head.t2,) + args)
        else:
            return cls(head=head, args=args)

    def evolve(self, head=None, args=None):
        if head is None:
            head = self.head
        if args is None:
            args = self.args
        return type(self).build(head=head, args=args)

    def to_term(self) -> Term:
        term = self.head
        for arg in self.args:
            term = term(arg)
        return term

    def stack(self, arg: Term):
        return self.evolve(args=self.args + (arg, ))

    # If None is returned, the reduction is terminated
    # outermost leftmost reduction.
    def reduce_or_none(self) -> Context | None:
        if isinstance(self.head, Abs) and len(self.args) > 0:
            head_substituted = self.head.t.subst(0, self.args[0]).shift(-1, 0)
            return self.evolve(head=head_substituted, args=self.args[1:])
        if isinstance(self.head, BuiltinFunction) and self.head.applicable_args(self.args):
            reduced, rest = self.head.apply_args(self.args)
            return self.evolve(head=reduced, args=rest)
        head_reduced = self.head.eval_or_none()
        if head_reduced is not None:
            return self.evolve(head=head_reduced)
        for i in range(len(self.args)):
            arg_reduced = self.args[i].eval_or_none()
            if arg_reduced is not None:
                new_args = self.args[0:i] + (arg_reduced,) + self.args[i + 1:]
                return self.evolve(args=new_args)
        else:
            return None


# Builtin data types
@frozen
class Data(Builtin, Generic[T], ABC):
    value: T = field(validator=helpers.not_none)

    @classmethod
    def nameless_repr(cls, value):
        assert hasattr(value, '__repr__')
        return cls.nameless(value=repr(value))

    @classmethod
    def nameless_str(cls, value):
        assert hasattr(value, '__str__')
        return cls.nameless(value=str(value))

    @classmethod
    def named_repr(cls, value):
        assert hasattr(value, '__repr__')
        return cls.named(value=repr(value))

    @classmethod
    def named_str(cls, value):
        assert hasattr(value, '__str__')
        return cls.named(value=str(value))

    def _eval_or_none(self):
        return None

    def _shift(self, d, c):
        return self

    def _subst_or_none(self, var, term):
        return None

    def _free_variables(self):
        return set()

    def _remove_name_with_context(self, _):
        return type(self).nameless(value=self.value)

    def _applicable_args(self, _):
        return False

    def _apply_args(self, _):
        assert False


class String(Data[str]):
    pass


class Integer(Data[int]):

    @classmethod
    def nameless_from_str(cls, string):
        assert isinstance(string, str)
        assert string.isdigit()
        return cls.nameless(value=int(string))

    @classmethod
    def named_from_str(cls, string):
        assert isinstance(string, str)
        assert string.isdecimal()
        return cls.named(value=int(string))


class Boolean(Data[bool]):
    pass


@frozen
class List(Unary):
    terms: tuple[Term, ...] = field(validator=helpers.not_none)
    name: str = 'List'

    def __attr_post_init__(self):
        assert all(isinstance(t, Term) for t in self.terms)
        assert len(self.terms) == 0 or all((t == self.is_named for t in self.terms))

    def _eval_or_none(self):
        evaluated = [term.eval_or_none() for term in self.terms]
        if all(t is None for t in evaluated):
            return None
        else:
            evaluated_expanded = (x[0] if x[1] is None else x[1] for x in zip(self.terms, evaluated))
            return evolve(self, terms=tuple(evaluated_expanded))

    def _shift(self, d, c):
        shifted = [t.shift(d, c) for t in self.terms]
        return evolve(self, terms=tuple(shifted))

    def _subst_or_none(self, num, term):
        subst = [t.subst_or_none(num, term) for t in self.terms]
        if all(t is None for t in subst):
            return None
        else:
            subst_expanded = (x[0] if x[1] is None else x[1] for x in zip(self.terms, subst))
            return evolve(self, terms=tuple(subst_expanded))

    def _free_variables(self):
        return set().union(*[t.free_variables() for t in self.terms])

    def _remove_name_with_context(self, context):
        return List.nameless(meta_info=self.meta_info,
                             terms=tuple(t.remove_name_with_context(context) for t in self.terms))

    def _applicable(self, term):
        return isinstance(term, Integer)

    def _apply_arg(self, term):
        return self.terms[term.value]


@frozen
class Record(Unary):
    name = 'Record'
    _attributes: dict[str, Term] = \
        field(validator=helpers.not_none)

    def __attr_post_init__(self):
        assert all(isinstance(k, str) for k in self.attributes().keys())
        assert all(isinstance(t, Term) for t in self.attributes().values())

    @classmethod
    def build(cls, is_named: bool, attributes: dict[str, Term]):
        return cls(is_named=is_named, attributes=attributes.copy())

    def evolve(self, is_named: bool | None = None, attributes: dict[str, Term] | None =None):
        if attributes is None:
            attributes = self._attributes
        if is_named is None:
            is_named = self.is_named
        return evolve(self, is_named=is_named, attributes=attributes.copy())

    def attributes(self):
        return self._attributes.copy()

    def _eval_or_none(self):
        evaluated = {label: t.eval_or_none() for label, t in self.attributes().items()}
        if all(t is None for _, t in evaluated.items()):
            return None
        else:
            evaluated_expand = dict(evaluated)
            for k in evaluated.keys():
                if evaluated_expand[k] is None:
                    evaluated_expand[k] = self.attributes()[k]
            return self.evolve(attributes=evaluated_expand)

    def _shift(self, d, c):
        shifted = dict((label, t.shift(d, c)) for label, t in self.attributes().items())
        return self.evolve(attributes=shifted)

    def _subst_or_none(self, num, term):
        subst = dict((label, t.subst_or_none(num, term)) for label, t in self.attributes().items())
        if all(t is None for _, t in subst.items()):
            return None
        else:
            for k in subst.keys():
                if subst[k] is None:
                    subst[k] = self._attributes[k]
            return self.evolve(attributes=subst)

    def _free_variables(self):
        return set().union(*(t.free_variables() for _, t in self.attributes().items()))

    def _remove_name_with_context(self, context):
        return self.evolve(
            attributes=dict((label, t.remove_name_with_context(context)) for label, t
                            in self.attributes().items()),
            is_named=False)

    def _applicable(self, term: Term):
        return isinstance(term, String) and term.value in self.attributes()

    def _apply_arg(self, term: String):
        return self.attributes()[term.value]
