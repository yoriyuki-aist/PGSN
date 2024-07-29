from __future__ import annotations
import helpers
from attrs import field, frozen, evolve
from lambda_term import Nameless, Named, Constant, Builtin, Abs, App
from record_term import Record
from list_term import List


# List related

empty_list = Constant(name='empty_list')


@frozen
class AddHead(Builtin):

    def applicable(self, arg):
        if not isinstance(arg, List):
            return False
        if not len(arg.terms) == 2:
            return False
        if not isinstance(arg.terms[1], List):
            return False
        return True

    def apply_arg(self, arg: List):
        assert isinstance(arg.terms[1], List)
        assert hasattr(arg.terms[1], 'terms')
        added = [arg.terms[0]] + arg.terms[1].terms
        return List(terms=added)


add_head = AddHead(name='list.add_head')


@frozen
class Head(Builtin):

    def applicable(self, arg: List):
        return len(arg.terms) >= 1

    def apply_arg(self, arg: List):
        return arg.terms[0]


head = Head(name='list.head')


class Tail(Builtin):

    def applicable(self, arg: List):
        return len(arg.terms) >= 1

    def apply_arg(self, arg: List):
        return List(terms=arg.terms[1:])


tail = Tail(name='list.tail')


@frozen
class Fold(Builtin):

    def applicable(self, arg: Record):
        args = arg.terms
        if not('fun' in args and 'init' in args and 'list' in args):
            return False
        return isinstance(args['list'], List)

    def apply_arg(self, arg: Record):
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
