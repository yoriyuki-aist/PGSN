from __future__ import annotations
import abc
from typing import TypeAlias
from attrs import field, frozen, evolve
from meta_info import MetaInfo
import helpers

Term: TypeAlias = "Term"
FreeVar: TypeAlias = "FreeVar"
Context: TypeAlias = dict[FreeVar, Term]

@frozen(kw_only=True)
class Term:
    meta_info: MetaInfo = MetaInfo.empty()

    @abc.abstractmethod
    def eval(self, context: Context) -> Term | None:
        pass

    @abc.abstractmethod
    def shift(self, num: int) -> Term:
        pass

    @abc.abstractmethod
    def subst(self, term: Term) -> Term:
        pass


@frozen
class Predefined(Term):
    __match_args__ = ('name',)
    name: str = field(validator=helpers.not_none)

    def eval(self, context):
        return None

    def shift(self, _):
        return self

    def subst(self, _):
        return self


goal = Predefined(name="Goal")
strategy = Predefined(name="Strategy")
evidence = Predefined(name="Evidence")
context = Predefined(name="Context")
assumption = Predefined(name="Assumption")


@frozen
class FreeVar(Term):
    __match_args__ = ('x',)
    x: str = field(validator=helpers.not_none)

    def eval(self, context):
        if self in context:
            return context[self]
        else:
            return None

    def shift(self, _):
        return self

    def subst(self, _):
        return self

@frozen
class BndVar(Term):
    __match_args__ = ('num',)
    num: int = field(validator=helpers.non_negative)

    def eval(self, context):
        return None

    def shift(self, shift_num):
        return evolve(self, num=self.num+shift_num)

    def subst(self, term):
        if self.num == 0:
            return term
        else:
            return self


@frozen
class Abs(Term):
    v: BndVar = field(validator=helpers.non_negative)
    t: Term = field(validator=helpers.not_none)

    @classmethod
    def abstract(cls, variable:FreeVar, term:Term):
        term = term.shift(1)
        bnd_var = BndVar(0)
        term = term.eval({variable: bnd_var})
        return cls(v=bnd_var, t=term)

    def eval(self, context):
        t_eval = self.t.eval(context)
        if t_eval is None:
            return None
        else:
            return evolve(self, t=t_eval)

    def shift(self, shift_num):
        return evolve(self, v=evolve(self.v, num=self.v.num+1), t=self.t.shift(1))

    def subst(self, term):
        return self


@frozen
class App(Term):
    t1: Term = field(validator=helpers.not_none)
    t2: Term = field(validator=helpers.not_none)

    def eval(self, context):
        t1_eval = self.t1.eval(context)
        t2_eval = self.t2.eval(context)
        t1_prime = helpers.default(t1_eval, self.t1)
        t2_prime = helpers.default(t2_eval, self.t1)
        if isinstance(t1_prime, Abs):
            return t1_prime.t.subst(t2_prime)
        else:
            if t1_eval is None and t2_eval is None:
                return None
            return evolve(self, t1=t1_prime, t2=t2_prime)

    def shift(self, shift_num):
        return App(t1=self.t1.shift(shift_num), t2=self.t2.shift(shift_num))

    def subst(self, term):
        return evolve(self, t1=self.t1.subst(term), t2=self.t2.subst(term))

