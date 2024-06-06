from __future__ import annotations
import abc
from typing import TypeAlias
from attrs import field, frozen, evolve, define
from meta_info import MetaInfo
import helpers

Term: TypeAlias = "Term"

@frozen(kw_only=True)
class Term:
    meta_info: MetaInfo = MetaInfo.empty()

    @abc.abstractmethod
    def eval_or_none(self) -> Term | None:
        pass

    def eval(self) -> Term:
        return helpers.default(self.eval_or_none(), self)

    @abc.abstractmethod
    def shift(self, num: int, cutoff: int) -> Term:
        pass

    @abc.abstractmethod
    def subst(self, variable: int, term: Term) -> Term:
        pass


@frozen
class Variable(Term):
    __match_args__ = ('num',)
    num: int = field(validator=helpers.non_negative)

    def eval_or_none(self):
        return self

    def shift(self, d, cutoff):
        if self.num < cutoff:
            return self
        else:
            return evolve(self, num=self.num+d)

    def subst(self, num, term):
        if self.num == num:
            return term
        else:
            return self


@frozen
class Abs(Term):
    t: Term = field(validator=helpers.not_none)

    def eval_or_none(self):
        reduced = self.t.eval_or_none()
        if reduced is None:
            return None
        else:
            return evolve(self, t=reduced)

    def shift(self, d, c):
        return evolve(self, t=self.t.shift(d, c+1))

    def subst(self, var, term):
        return evolve(self, t=self.t.subst(var, term))


@frozen
class App(Term):
    t1: Term = field(validator=helpers.not_none)
    t2: Term = field(validator=helpers.not_none)

    def eval_or_none(self):
        t1_eval = self.t1.eval_or_none()
        t2_eval = self.t2.eval_or_none()
        t1_prime = helpers.default(t1_eval, self.t1)
        t2_prime = helpers.default(t2_eval, self.t1)
        if isinstance(t1_prime, Abs):
            t2_shifted = self.t2.shift(1, 0)
            t_substituted = self.t1.subst(0, t2_shifted)
            return t_substituted.shift(-1, 0)
        else:
            if t1_eval is None and t2_eval is None:
                return None
            return evolve(self, t1=t1_prime, t2=t2_prime)

    def shift(self, d, c):
        return App(t1=self.t1.shift(d, c), t2=self.t2.shift(d, c))

    def subst(self, var, term):
        return evolve(self, t1=self.t1.subst(var, term), t2=self.t2.subst(var, term))


