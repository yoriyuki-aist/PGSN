from __future__ import annotations
import helpers
from attrs import field, frozen, evolve
from lambda_term import Nameless, Named, Constant, Builtin, Abs, App

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
