from __future__ import annotations
import helpers
from attrs import field, frozen, evolve
from lambda_term import Nameless, Named


@frozen
class DataNameless(Nameless):
    value: any = field(validator=helpers.not_none)

    def eval_or_none(self):
        return None

    def shift(self, d, c):
        return self

    def subst_or_none(self, var, term):
        return None

    def recover_name_with_context(self, context, default_name='x'):
        return DataNamed(self.value)


@frozen
class DataNamed(Named):
    value: any = field(validator=helpers.not_none)

    def free_variables(self):
        return set()

    def remove_name_with_context(self, _):
        return DataNameless(self.value)
