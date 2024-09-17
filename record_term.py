from __future__ import annotations
import helpers
from attrs import field, frozen, evolve
from lambda_term import Term
import meta_info as meta
from meta_info import MetaInfo
from data_term import String


@frozen
class Record(Term):
    terms: tuple[tuple[str, Term]] = \
        field(default=tuple(), validator=helpers.not_none)

    def __attr_post_init__(self):
        assert len(self.terms) == 0 or all((t == self.is_named for k, t in self.terms))

    @classmethod
    def named(cls, terms: tuple[tuple[str, Term]] = tuple(), meta_info: MetaInfo = meta.empty):
        assert all((t[1].is_named for t in terms))
        return Record(terms=terms, is_named=True)

    @classmethod
    def nameless(cls, terms: tuple[tuple[str, Term]] = tuple(), meta_info: MetaInfo = meta.empty):
        assert all((not t[1].is_named for t in terms))
        return Record(terms=terms, is_named=False)

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
        return Record.nameless(tuple((label, t.remove_name_with_context(context)) for label, t in self.terms),
                               meta_info=self.meta_info)

    def evolve(self, terms: tuple[tuple[str, Term]]):
        return evolve(self, terms=terms)

    def _applicable(self, term):
        return isinstance(term, String) and helpers.contains(term.value, self.terms)

    def _apply_arg(self, term):
        assert isinstance(term, String) and helpers.contains(term.value, self.terms)
        return helpers.query(self.terms, term.value)


empty = Record.named(tuple())
