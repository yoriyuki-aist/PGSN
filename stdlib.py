from __future__ import annotations
import helpers
from typing import Any
from attrs import field, frozen, evolve
from lambda_term import Constant, BuiltinFunction, Abs, App, Term, Unary
from record_term import Record
from list_term import List
from data_term import String, Integer


def check_type_list(arg: Term, types: list):
    if not isinstance(arg, List):
        return False
    return helpers.check_type_list(arg.terms, types)


def check_type_dict(arg: Term, types: dict):
    if not isinstance(arg, Record):
        return False
    return helpers.check_type_list(arg.terms, types)


# List related
empty_list = List.named(terms=[])


@frozen
class Cons(BuiltinFunction):
    arity=2

    def _applicable_args(self, args: tuple[Term]):
        return isinstance(args[1], List)

    def _apply_args(self, args: tuple[Term]):
        return args[1].evolve(terms=(args[0],) + args[1])


cons = Cons.named(name='stdlib.cons')


@frozen
class Head(Unary):

    def _applicable(self, arg: Term):
        return isinstance(arg, List) and len(arg.terms) >= 1

    def _apply_arg(self, arg: List) -> Term:
        return arg.terms[0]


head = Head.named(name='stdlib.head')


@frozen
class Tail(Unary):

    def _applicable(self, arg: Term):
        return isinstance(arg, List) and len(arg.terms) >= 1

    def _apply_arg(self, arg: List) -> List:
        return List(terms=arg.terms[1:], is_named=self.is_named)


tail = Tail.named(name='stdlib.tail')


class Index(BuiltinFunction):
    arity=2

    def _applicable_args(self, args: tuple[Term]):
        return isinstance(args[0], List) and isinstance(args[1], Integer)

    def _apply_args(self, args: tuple[Term]) -> Term:
        return args[0].terms[args[1].value]


index = Index.named(name='stdlib.indexing')


@frozen
class Fold(BuiltinFunction):
    arity = 3

    def _applicable_args(self, args: tuple(Term)):
        if not len(args) >= 3:
            return False
        if not isinstance(args[2], List):
            return False
        return True

    def _apply_args(self, args: tuple[Term]) -> Term:
        fun = args[0]
        init = args[1]
        arg_list = args[2].terms
        if len(arg_list) == 0:
            return init
        list_head = arg_list[0]
        list_rest = arg_list[1:]
        rest = List(terms=list_rest, is_named=self.is_named)
        return fun(list_head)(self(fun)(init)(rest))


fold = Fold.named(name='stdlib.fold')


@frozen
class Map(BuiltinFunction):
    arity=2

    def _applicable_args(self, args: tuple[Term]):
        if not isinstance(args[2], List):
            return False
        return True

    def _apply_args(self, args: tuple[Term]) -> Term:
        fun = args[0]
        arg = args[1]
        arg_list = arg.terms
        map_list = tuple((fun(t) for t in arg_list))

        map_result = List(terms=map_list, is_named=self.is_named)
        return map_result


map_term = Map.named(name='stlib.map')
