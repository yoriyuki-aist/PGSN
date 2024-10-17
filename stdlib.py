from __future__ import annotations
import helpers
from typing import Sequence
from attrs import frozen, evolve, field
from lambda_term import BuiltinFunction, Term, Unary, Variable
import lambda_term
from record_term import Record
from list_term import List
from data_term import Integer, Boolean
import data_term
from object_term import ObjectTerm, ClassTerm


def check_type_list(arg: Term, types: list):
    if not isinstance(arg, List):
        return False
    return helpers.check_type_list(arg.terms, types)


def check_type_dict(arg: Term, types: dict):
    if not isinstance(arg, Record):
        return False
    return helpers.check_type_list(arg.attributes, types)


# List functions

@frozen
class Cons(BuiltinFunction):
    name = 'Cons'
    arity = 2

    def _applicable_args(self, args: Sequence[Term]):
        return isinstance(args[1], List)

    def _apply_args(self, args: tuple[Term, List]):
        return evolve(args[1], terms=(args[0],) + args[1].terms)


cons = Cons.named()


@frozen
class Head(Unary):
    name = 'Head'

    def _applicable(self, arg: List):
        return isinstance(arg, List) and len(arg.terms) >= 1

    def _apply_arg(self, arg: List) -> Term:
        return arg.terms[0]


head = Head.named()


@frozen
class Tail(Unary):
    name = 'Tail'

    def _applicable(self, arg: List):
        return isinstance(arg, List) and len(arg.terms) >= 1

    def _apply_arg(self, arg: List) -> List:
        return List(terms=arg.terms[1:], is_named=self.is_named)


tail = Tail.named()


class Index(BuiltinFunction):
    name = 'Index'
    arity = 2

    def _applicable_args(self, args: Sequence[Term]):
        return isinstance(args[0], List) and isinstance(args[1], Integer)

    def _apply_args(self, args: tuple[Term]) -> Term:
        return args[0].terms[args[1].value]


index = Index.named()


@frozen
class Fold(BuiltinFunction):
    name = 'Fold'
    arity = 3

    def _applicable_args(self, args: Sequence[Term]):
        if not len(args) >= 3:
            return False
        if not isinstance(args[2], List):
            return False
        return True

    def _apply_args(self, args: Sequence[Term]) -> Term:
        fun = args[0]
        init = args[1]
        arg_list = args[2].terms
        if len(arg_list) == 0:
            return init
        list_head = arg_list[0]
        list_rest = arg_list[1:]
        rest = List(terms=list_rest, is_named=self.is_named)
        return fun(list_head)(self(fun)(init)(rest))


fold = Fold.named()


@frozen
class Map(BuiltinFunction):
    name = 'Map'
    arity = 2

    def _applicable_args(self, args: Sequence[Term]):
        if not isinstance(args[1], List):
            return False
        return True

    def _apply_args(self, args: Sequence[Term]) -> Term:
        fun = args[0]
        arg = args[1]
        arg_list = arg.terms
        map_list = tuple((fun(t) for t in arg_list))
        map_result = List(terms=map_list, is_named=self.is_named)
        return map_result


map_term = Map.named()


# Integer functions
@frozen
class Plus(BuiltinFunction):
    arity = 2
    name = 'Plus'

    def _applicable_args(self, args: tuple[Term, ...]):
        return len(args) >= 2 and isinstance(args[0], Integer) and isinstance(args[1], Integer)

    def _apply_args(self, args: tuple[Term, ...]):
        i1 = args[0].value
        i2 = args[1].value
        return data_term.Integer.nameless(value=i1+i2)


plus = Plus.named()


integer_sum = fold(plus)(data_term.integer(0))


# multi_arg function
@frozen
class MultiArgFunction(BuiltinFunction):
    # Hack: arity has a default argument but the default value is invalid.
    # The object must be created by build class method.
    arity = field(default=0)
    _keyword_args: dict[str, Term | None] = field(default={})
    # Hack: syntactically, body is an optional argument but must be specified otherwise
    # the runtime error occurs.
    main: Term | None = field(default=None, validator=helpers.not_none)

    def __attr_post_init__(self):
        assert all((var.is_named == self.is_named for var in self.positional_variable))
        assert all((var.is_named == self.is_named for var  in self._keyword_variable.keys()))
        assert all((t is None or t.is_named == self.is_named for _, t in self._keyword_variable.items()))
        assert self.main is not None
        assert self.arity >= 1

    @classmethod
    def build(cls,
              is_named: bool,
              positional_vars: tuple[Variable, ...],
              keyword_args: dict[str, Term | None],
              body: Term):
        keywords = sorted(keyword_args.keys())
        main = body
        for key in keywords:
            var = lambda_term.variable(key)
            main = lambda_term.lambda_abs(var, main)
        var_r = lambda_term.variable('r')
        for key in reversed(keywords):
            s = data_term.string(key)
            main = main(var_r(s))
        main = lambda_term.lambda_abs(var_r, main)
        for var in reversed(positional_vars):
            main = lambda_term.lambda_abs(var, main)
        return cls(is_named=is_named,
                   arity=len(positional_vars) + 1,
                   keyword_args=keyword_args.copy(),
                   main=main)

    def _remove_name_with_context(self, context: list[str]) -> Term:
        keyword_args = {k: t.remove_name_with_context(context) if t is not None else None for k, t in self._keyword_args.items()}
        main = self.main.remove_name_with_context(context)
        return self.evolve(is_named=False, keyword_args=keyword_args, main=main)

    def _applicable_args(self, args: tuple[Term,...]) -> bool:
        if not isinstance(args[self.arity-1], Record):
            return False
        r = args[self.arity-1].attributes()
        for k, v in self._keyword_args.items():
            if v is None and k not in r:
                return False
        return True

    def _apply_args(self, args: tuple[Term,...]):
        r = args[self.arity - 1].attributes()
        for k, v in self._keyword_args.items():
            if k not in r and v is not None:
                r[k] = v
        assert set(self._keyword_args.keys()).issubset(set(r.keys()))
        assert all(v is not None for v in r.values())
        r_term = Record.nameless(attributes=r)
        t = self.main
        for arg in args[:-1]:
            t = t(arg)
        return t(r_term)


def multi_arg_function(positional_vars: tuple[Variable,...], keyword_args: dict[str, Term | None], body: Term):
    return MultiArgFunction.named(positional_vars=positional_vars,
                                  keyword_args=keyword_args,
                                  body=body)


# let var = t1 in t2
def let(var: Variable, t1: Term, t2: Term):
    return (lambda_term.lambda_abs(var, t2))(t1)


# Boolean

class IfThenElse(BuiltinFunction):
    arity = 3
    name = 'IfThenElse'

    def _applicable_args(self, terms: tuple[Term,...]):
        return isinstance(terms[0], Boolean)

    def _apply_args(self, terms: tuple[Term,...]):
        b = terms[0].value
        return terms[1] if b else terms[2]


if_then_else = IfThenElse.named()


# guard b t only progresses b is true
class Guard(BuiltinFunction):
    arity=2
    name='Guard'

    def _applicable_args(self, terms: tuple[Term,...]):
        return isinstance(terms[0], Boolean) and terms[0].value

    def _apply_args(self, terms: tuple[Term,...]):
        return terms[1]


guard = Guard.named()







