from __future__ import annotations
import helpers
from attrs import field, frozen, evolve
from lambda_term import Term, Unary
from data_term import String


@frozen
class Record(Unary):
    name = 'Record'
    _terms: dict[str, Term] = \
        field(default={}, validator=helpers.not_none)

    @classmethod
    def named(cls, terms: dict[str, Term]):
        return cls(is_named=True, terms=terms.copy())

    @classmethod
    def nameless(cls, terms: dict[str, Term]):
        return cls(is_named=True, terms=terms.copy())

    def __attr_post_init__(self):
        assert len(self._terms) == 0 or all((t == self.is_named for k, t in self._terms.items()))

    def evolve(self, is_named: bool | None = None, terms: dict[str, Term] | None =None):
        if terms is None:
            terms = self._terms
        if is_named is None:
            is_named = self.is_named
        return evolve(self, is_named=is_named, terms=terms)

    def terms(self):
        return self._terms.copy()

    def _eval_or_none(self):
        evaluated = ((label, t.eval_or_none()) for label, t in self._terms.items())
        if all(t is None for _, t in evaluated):
            return None
        else:
            evaluated_expand = dict((k,  y if x is None else x) for (k, x), (k, y) in zip(evaluated, self._terms.items()))
            return self.evolve(terms=evaluated_expand)

    def _shift(self, d, c):
        shifted = dict((label, t.shift(d, c)) for label, t in self._terms.items())
        return self.evolve(terms=shifted)

    def _subst_or_none(self, num, term):
        subst = ((label, t.subst_or_none(num, term)) for label, t in self._terms.items())
        if all(t is None for _, t in subst):
            return None
        else:
            subst_expand = dict((k, y if x is None else x) for (k, x), (k, y) in zip(subst, self._terms.items()))
            return self.evolve(terms=subst_expand)

    def _free_variables(self):
        return set().union(*(t.free_variables() for _, t in self._terms.items()))

    def _remove_name_with_context(self, context):
        return self.evolve(terms=dict((label, t.remove_name_with_context(context)) for label, t in self._terms.items()),
                           is_named=False)

    def _applicable(self, term: String):
        return isinstance(term, String) and term.value in self._terms

    def _apply_arg(self, term: String):
        return self._terms[term.value]
