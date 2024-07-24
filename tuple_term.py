import helpers
from attrs import field, frozen, evolve
from lambda_term import Nameless, Named

@frozen
class Tuple(Nameless):
    terms: tuple[Nameless] = field(validator=helpers.not_none)

    def _check_terms(self, attribute, value):
        assert len(value) == self.num

    def eval_or_none(self):
        evaluated = tuple(t.eval_or_none() for t in self.terms)
        if all(t is None for t in evaluated):
            return None
        else:
            return evolve(self, terms=evaluated)

    def shift(self, d, c):
        shifted = tuple(t.shift(d, c) for t in self.terms)
        return evolve(self, terms=shifted)

    def subst_or_none(self, num, term):
        subst = tuple(t.subst_or_none(num, term) for t in self.terms)
        if all(t is None for t in subst):
            return None
        else:
            return evolve(self, terms=subst)

    def recover_name_with_context(self, context, default):
        return TupleNamed(terms=tuple(t.recover_name_with_context(context, default) for t in self.terms),
                          meta_info=self.meta_info)


@frozen
class TupleNamed(Named):
    terms: tuple[Named] = field(default={},
                               validator=helpers.not_none)

    def free_variables(self):
        return set().union(*{t.free_variables() for t in self.terms.values()})

    def remove_name_with_context(self, context):
        return Tuple(terms=tuple(t.remove_name_with_context(context) for t in self.terms),
                     meta_info=self.meta_info)
