from __future__ import annotations
import helpers
from attrs import field, frozen
from lambda_term import Term, Unary
from data_term import String


@frozen
class Record(Unary):
    name = 'Record'
    terms: tuple[tuple[str, Term], ...] = \
        field(default=tuple(), validator=helpers.not_none)

    def __attr_post_init__(self):
        assert len(self.terms) == 0 or all((t == self.is_named for k, t in self.terms))

    def _eval_or_none(self):
        evaluated = tuple((label, t.eval_or_none()) for label, t in self.terms)
        if all(t is None for _, t in evaluated):
            return None
        else:
            evaluated_expand = tuple((k,  y if x is None else x) for (k, x), (k, y) in zip(evaluated, self.terms))
            return self.evolve(terms=evaluated_expand)

    def _shift(self, d, c):
        shifted = tuple((label, t.shift(d, c)) for label, t in self.terms)
        return self.evolve(terms=shifted)

    def _subst_or_none(self, num, term):
        subst = ((label, t.subst_or_none(num, term)) for label, t in self.terms)
        if all(t is None for _, t in subst):
            return None
        else:
            subst_expand = tuple((k, y if x is None else x) for (k, x), (k, y) in zip(subst, self.terms))
            return self.evolve(terms=subst_expand)

    def _free_variables(self):
        return set().union(*(t.free_variables() for _, t in self.terms))

    def _remove_name_with_context(self, context):
        return self.evolve(terms=tuple((label, t.remove_name_with_context(context)) for label, t in self.terms),
                           is_named=False)

    def _applicable(self, term: String):
        return isinstance(term, String) and helpers.contains(term.value, self.terms)

    def _apply_arg(self, term: String):
        return helpers.query(self.terms, term.value)
