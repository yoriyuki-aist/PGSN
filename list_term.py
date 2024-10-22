from __future__ import annotations
import helpers
from attrs import field, frozen, evolve
from lambda_term import Term, Unary
from data_term import Integer


# List

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


# lambda term for API
empty = List.named(terms=tuple())


def list_term(terms: tuple[Term,...]):
    return List.named(terms=terms)
