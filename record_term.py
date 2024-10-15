from __future__ import annotations
import helpers
from attrs import field, frozen, evolve
from lambda_term import Term, Unary
from data_term import String


@frozen
class Record(Unary):
    name = 'Record'
    _attributes: dict[str, Term] = \
        field(default={}, validator=helpers.not_none)

    def __attr_post_init__(self):
        assert all(isinstance(k, str) for k in self._attributes.keys())
        assert all(isinstance(t, Term) for t in self._attributes.values())

    @classmethod
    def named(cls, attributes: dict[str, Term]):
        return cls(is_named=True, attributes=attributes.copy())

    @classmethod
    def nameless(cls, attributes: dict[str, Term]):
        return cls(is_named=False, attributes=attributes.copy())

    def __attr_post_init__(self):
        assert len(self._attributes) == 0 or all((t == self.is_named for k, t in self._attributes.items()))

    def evolve(self, is_named: bool | None = None, attributes: dict[str, Term] | None =None):
        if attributes is None:
            attributes = self._attributes
        if is_named is None:
            is_named = self.is_named
        return evolve(self, is_named=is_named, attributes=attributes)

    def terms(self):
        return self._attributes.copy()

    def _eval_or_none(self):
        evaluated = ((label, t.eval_or_none()) for label, t in self._attributes.items())
        if all(t is None for _, t in evaluated):
            return None
        else:
            evaluated_expand = dict((k,  y if x is None else x) for (k, x), (k, y) in zip(evaluated, self._attributes.items()))
            return self.evolve(attributes=evaluated_expand)

    def _shift(self, d, c):
        shifted = dict((label, t.shift(d, c)) for label, t in self._attributes.items())
        return self.evolve(attributes=shifted)

    def _subst_or_none(self, num, term):
        subst = ((label, t.subst_or_none(num, term)) for label, t in self._attributes.items())
        if all(t is None for _, t in subst):
            return None
        else:
            subst_expand = dict((k, y if x is None else x) for (k, x), (k, y) in zip(subst, self._attributes.items()))
            return self.evolve(attributes=subst_expand)

    def _free_variables(self):
        return set().union(*(t.free_variables() for _, t in self._attributes.items()))

    def _remove_name_with_context(self, context):
        return self.evolve(
            attributes=dict((label, t.remove_name_with_context(context)) for label, t in self._attributes.items()),
            is_named=False)

    def _applicable(self, term: Term):
        return isinstance(term, String) and term.value in self._attributes

    def _apply_arg(self, term: String):
        return self._attributes[term.value]


def record(d: dict[str, Term]):
    return Record.named(d)
