from __future__ import annotations
from collections.abc import Iterable
import helpers
from attrs import field, frozen, evolve
from meta_info import MetaInfo
import meta_info as meta
from lambda_term import Term, Constant, BuiltinFunction, Abs, App, Builtin
from data_term import String, Integer

# Arbitrary Python data


# List

@frozen
class List(Builtin):
    terms: tuple[Term] = field(validator=helpers.not_none)

    # @classmethod
    # def nameless(cls, terms: Iterable[Term] = tuple(), meta_info: MetaInfo = meta.empty):
    #     assert all((not t.is_named for t in terms))
    #     return List(terms=tuple(terms), is_named=False)
    #
    # @classmethod
    # def named(cls, terms: Iterable[Term] = tuple(), meta_info: MetaInfo = meta.empty):
    #     assert all((t.is_named for t in terms))
    #     return List(terms=tuple(terms), is_named=True)
    #
    def __attr_post_init__(self):
        assert len(self.terms) == 0 or all((t == self.is_named for t in self.terms))

    def evolve(self, terms):
        assert len(terms) == 0 or all((t == terms[0].is_named for t in terms))
        return evolve(self, terms=terms)

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
        return List.nameless(meta_info=self.meta_info, terms=[t.remove_name_with_context(context) for t in self.terms])

    def _applicable_args(self, terms):
        return False

    def _apply_args(self, terms):
        assert False


# Constant
empty = List.named(terms=tuple())