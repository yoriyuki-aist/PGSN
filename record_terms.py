from __future__ import annotations
import helpers
from attrs import field, frozen, evolve
from lambda_term import Nameless, Named


@frozen
class RecordNameless(Nameless):
    terms: dict[str, Nameless] = field(default={},
                                  validator=helpers.not_none)

    def eval_or_none(self):
        evaluated = {label: t.eval_or_none() for label, t in self.terms.items()}
        if all(t is None for t in evaluated.values()):
            return None
        else:
            return evaluated

    def shift(self, d, c):
        shifted = {label: t.shift(d, c) for label, t in self.terms.items()}
        return evolve(self, terms=shifted)

    def subst_or_none(self, num, term):
        subst = {label: t.subst_or_none(num, term) for label, t in self.terms.items()}
        if all(t is None for t in subst.values()):
            return None
        else:
            return subst

    def recover_name_with_context(self, context, default):
        return RecordNamed({label: t.recover_name_with_context(context, default) for label, t in self.terms.items()})


@frozen
class RecordNamed(Named):
    terms: dict[str, Named] = field(default={},
                               validator=helpers.not_none)

    def free_variables(self):
        return set().union(*{t.free_variables() for t in self.terms.values()})

    def remove_name_with_context(self, context):
        return RecordNameless({label: t.remove_name_with_context(context) for label, t in self.terms.items()})
