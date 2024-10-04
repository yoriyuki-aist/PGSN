from __future__ import annotations
import helpers
from typing import Sequence
from attrs import field, frozen, evolve
from lambda_term import Constant, BuiltinFunction, Abs, App, Term, Unary
import lambda_term
from record_term import Record
from list_term import List
from data_term import String, Integer
import data_term


def check_type_list(arg: Term, types: list):
    if not isinstance(arg, List):
        return False
    return helpers.check_type_list(arg.terms, types)


def check_type_dict(arg: Term, types: dict):
    if not isinstance(arg, Record):
        return False
    return helpers.check_type_list(arg.terms, types)


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
        if not isinstance(args[2], List):
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


# @frozen
# class Plus(BuiltinFunction):
#     arity = 2
#     name = 'Plus'
#
#     def _applicable_args(self, args: tuple[Term, ...]):
#         return len(args) >= 2 and isinstance(args[0], Integer) and isinstance(args[0], Integer)
#
#     def _apply_args(self, args: tuple[Term, ...]):
#         i1 = args[0].value
#         i2 = args[1].value
#         return data_term.integer(i1*i2)
#
#
# plus = Plus.named()
#
#
# _var_x = lambda_term.variable('x')
# _var_y = lambda_term.variable('y')
# _fun = lambda_term.lambda_abs(_var_x, lambda_term.lambda_abs(_var_y, plus(_var_x)(_var_y)))
# _var_z = lambda_term.variable('z')
# integer_sum = lambda_term.lambda_abs(_var_z, fold(_fun)(data_term.integer(0)))




