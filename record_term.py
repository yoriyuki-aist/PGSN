from __future__ import annotations
import helpers
from attrs import field, frozen, evolve
from lambda_term import Term, Unary, String


@frozen
class Record(Unary):
    name = 'Record'
    _attributes: dict[str, Term] = \
        field(validator=helpers.not_none)

    def __attr_post_init__(self):
        assert all(isinstance(k, str) for k in self.attributes().keys())
        assert all(isinstance(t, Term) for t in self.attributes().values())

    @classmethod
    def build(cls, is_named: bool, attributes: dict[str, Term]):
        return cls(is_named=is_named, attributes=attributes.copy())

    def evolve(self, is_named: bool | None = None, attributes: dict[str, Term] | None =None):
        if attributes is None:
            attributes = self._attributes
        if is_named is None:
            is_named = self.is_named
        return evolve(self, is_named=is_named, attributes=attributes.copy())

    def attributes(self):
        return self._attributes.copy()

    def _eval_or_none(self):
        evaluated = {label: t.eval_or_none() for label, t in self.attributes().items()}
        if all(t is None for _, t in evaluated.items()):
            return None
        else:
            evaluated_expand = dict(evaluated)
            for k in evaluated.keys():
                if evaluated_expand[k] is None:
                    evaluated_expand[k] = self.attributes()[k]
            return self.evolve(attributes=evaluated_expand)

    def _shift(self, d, c):
        shifted = dict((label, t.shift(d, c)) for label, t in self.attributes().items())
        return self.evolve(attributes=shifted)

    def _subst_or_none(self, num, term):
        subst = dict((label, t.subst_or_none(num, term)) for label, t in self.attributes().items())
        if all(t is None for _, t in subst.items()):
            return None
        else:
            for k in subst.keys():
                if subst[k] is None:
                    subst[k] = self._attributes[k]
            return self.evolve(attributes=subst)

    def _free_variables(self):
        return set().union(*(t.free_variables() for _, t in self.attributes().items()))

    def _remove_name_with_context(self, context):
        return self.evolve(
            attributes=dict((label, t.remove_name_with_context(context)) for label, t
                            in self.attributes().items()),
            is_named=False)

    def _applicable(self, term: Term):
        return isinstance(term, String) and term.value in self.attributes()

    def _apply_arg(self, term: String):
        return self.attributes()[term.value]


def record(d: dict[str, Term]):
    return Record.named(attributes=d)
