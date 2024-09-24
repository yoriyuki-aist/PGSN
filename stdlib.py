from __future__ import annotations
import helpers
from typing import Any
from attrs import field, frozen, evolve
from lambda_term import Constant, BuiltinFunction, Abs, App, Term
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
class AddHead(BuiltinFunction):
    head: Term = field(validator=helpers.not_none)

    def _applicable(self, arg: Term):
        return isinstance(arg, List)

    def _apply_args(self, arg: List) -> List:
        added = (self.head,) + arg.terms
        return List(terms=added, is_named=self.is_named)


@frozen
class Cons(BuiltinFunction):

    def _applicable(self, arg: Term):
        return True

    def _apply_args(self, arg: Term):
        return AddHead(head=arg, is_named=self.is_named)


cons = Cons.named(name='stdlib.cons')


@frozen
class Head(BuiltinFunction):

    def _applicable(self, arg: Term):
        return isinstance(arg, List) and len(arg.terms) >= 1

    def _apply_args(self, arg: List) -> Term:
        return arg.terms[0]


head = Head.named(name='stdlib.head')


@frozen
class Tail(BuiltinFunction):

    def _applicable(self, arg: Term):
        return isinstance(arg, List) and len(arg.terms) >= 1

    def _apply_args(self, arg: List) -> List:
        return List(terms=arg.terms[1:], is_named=self.is_named)


tail = Tail.named(name='stdlib.tail')


@frozen
class Query(BuiltinFunction):
    queried_list: tuple[Term] = field(validator=helpers.not_none)

    def _applicable(self, arg: Term):
        if not isinstance(arg, Integer):
            return False
        i = int(arg.value)
        return 0 <= i < len(self.queried_list)

    def _apply_args(self, arg: Integer) -> Term:
        i = int(arg.value)
        return self.queried_list[i]


class Index(BuiltinFunction):

    def _applicable(self, arg: Term):
        return isinstance(arg, List)

    def _apply_args(self, arg: List) -> Query:
        return Query(queried_list=arg.terms)


index = Index.named(name='stdlib.indexing')


@frozen
class Fold(BuiltinFunction):

    def _applicable(self, arg: Term):
        if not isinstance(arg, Record):
            return False
        if not helpers.contains('fun', arg.terms):
            return False
        if not helpers.contains('init', arg.terms):
            return False
        if not helpers.contains('list', arg.terms):
            return False
        arg = helpers.query(arg.terms, 'list')
        if not isinstance(arg, List):
            return False
        return True

    def _apply_args(self, arg: Record) -> Term:
        assert self.applicable(arg)
        fun = helpers.query(arg.terms, 'fun')
        init = helpers.query(arg.terms, 'init')
        arg = helpers.query(arg.terms, 'list')
        arg_list = arg.terms
        if len(arg_list) == 0:
            return init
        list_head = arg_list[0]
        list_rest = arg_list[1:]
        rest = List(terms=list_rest, is_named=self.is_named)
        new_fold_args = Record(terms=(('fun', fun), ('init', init), ('list', rest)),
                                         meta_info=self.meta_info, is_named=self.is_named)
        new_fold = App(self, new_fold_args, is_named=self.is_named)
        new_args = List((list_head, new_fold), is_named=self.is_named)
        return App(fun, new_args, is_named=self.is_named)


fold = Fold.named(name='stdlib.fold')


@frozen
class Map(BuiltinFunction):

    def _applicable(self, arg: Term):
        if not isinstance(arg, Record):
            return False
        if not helpers.contains('fun', arg.terms):
            return False
        if not helpers.contains('list', arg.terms):
            return False
        arg = helpers.query(arg.terms, 'list')
        if not isinstance(arg, List):
            return False
        return True

    def _apply_args(self, arg: Record) -> Term:
        assert self.applicable(arg)
        fun = helpers.query(arg.terms, 'fun')
        arg = helpers.query(arg.terms, 'list')
        arg_list = arg.terms
        map_list = tuple(App(fun, t, is_named=self.is_named) for t in arg_list)
        map_result = List(terms=map_list, is_named=self.is_named)
        return map_result


map_term = Map.named(name='stlib.map')
