from __future__ import annotations
import helpers
from attrs import field, frozen, evolve
from lambda_term import Nameless, Named, Constant, Builtin, Abs, App
from tuple_term import Tuple
from record_term import Record

# Arbitrary Python data


# List

@frozen
class List(Nameless):
    terms: list[Nameless] = field(validator=helpers.not_none)

    def eval_or_none(self):
        evaluated = [term.eval_or_none() for term in self.terms]
        if all(t is None for t in evaluated):
            return None
        else:
            return evolve(self, terms=evaluated)

    def shift(self, d, c):
        shifted = [t.shift(d, c) for t in self.terms]
        return evolve(self, terms=shifted)

    def subst_or_none(self, num, term):
        subst = [t.subst_or_none(num, term) for t in self.terms]
        if all(t is None for t in subst):
            return None
        else:
            return subst

    def recover_name_with_context(self, context, default):
        return ListNamed(meta_info=self.meta_info,
                         terms=[t.recover_name_with_context(context, default) for t in self.terms])


@frozen
class ListNamed(Named):
    terms: list[Named] = field(default=[],
                               validator=helpers.not_none)

    def free_variables(self):
        return set().union(*{t.free_variables() for t in self.terms})

    def remove_name_with_context(self, context):
        return List(meta_info=self.meta_info, terms=[t.remove_name_with_context(context) for t in self.terms])


# Constant
empty_list = Constant(name='empty_list')


# Functions
@frozen
class AddHead(Builtin):

    def applicable(self, arg: Tuple):
        if not len(arg.terms) == 2:
            return False
        if not isinstance(arg.terms[1], List):
            return False
        return True

    def apply_arg(self, arg: Tuple):
        added = [arg.terms[0]] + arg.terms[1].terms
        return List(terms=added)


add_head = AddHead(name='list.add_head')


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
        new_fold = Record(terms={'fun': fun, 'init': init, 'list': list_tail},
                          meta_info=self.meta_info)
        new_arg = Tuple(terms=(list_head, new_fold))
        return App(add_head, new_arg)


fold = Fold(name='list.hold')
