from __future__ import annotations
import helpers
from typing import Any
from attrs import field, frozen, evolve
from lambda_term import Nameless, Named, Constant, Builtin, Abs, App
from record_term import Record
from list_term import List
from string_term import String


def check_type_list(arg: Nameless, types: list):
    if not isinstance(arg, List):
        return False
    return helpers.check_type_list(arg.terms, types)


def check_type_dict(arg: Nameless, types: dict):
    if not isinstance(arg, Record):
        return False
    return helpers.check_type_list(arg.terms, types)


# List related
empty_list = List(terms=[])


@frozen
class AddHead(Builtin):

    def applicable(self, arg: Nameless):
        return check_type_list(arg, [Nameless, List])

    def _apply_arg(self, arg: List) -> List:
        added = [arg.terms[0]] + arg.terms[1].terms
        return List(terms=added)


add_head = AddHead(name='list.add_head')


@frozen
class Head(Builtin):

    def applicable(self, arg: Nameless):
        return isinstance(arg, List) and len(arg.terms) >= 1

    def _apply_arg(self, arg: List) -> Nameless:
        return arg.terms[0]


head = Head(name='list.head')


@frozen
class Tail(Builtin):

    def applicable(self, arg: Nameless):
        return isinstance(arg, List) and len(arg.terms) >= 1

    def _apply_arg(self, arg: List) -> List:
        return List(terms=arg.terms[1:])


tail = Tail(name='list.tail')


@frozen
class Index(Builtin):

    def applicable(self, arg: Nameless):
        if not check_type_list(arg, [List, String]):
            return False
        if not str.isdigit(arg.terms[1].value):
            return False
        i = int(arg.terms[1].value)
        if not (0 <= i < len(arg.terms[0].terms)):
            return False
        return True

    def _apply_arg(self, arg:List) -> Nameless:
        i = int(arg.terms[1].value)
        return arg.terms[0].terms[i]


index = Index(name='list.indexing')


@frozen
class Fold(Builtin):

    def applicable(self, arg: Nameless):
        return check_type_dict(arg, {'fun': Any, 'init': Any, 'list': List})

    def _apply_arg(self, arg: Record) -> Nameless:
        fun = arg.terms['fun']
        init = arg.terms['init']
        arg_list = arg.terms['list'].terms
        if len(arg_list) == 0:
            return init
        list_head = arg_list[0]
        list_tail = arg_list[1:]
        new_fold_args = Record(terms={'fun': fun, 'init': init, 'list': list_tail}, meta_info=self.meta_info)
        new_fold = App(self, new_fold_args)
        new_args = List([list_head, new_fold])
        return App(fun, new_args)


fold = Fold(name='list.fold')
