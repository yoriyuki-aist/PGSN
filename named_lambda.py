from __future__ import annotations
import abc
from typing import TypeAlias
from attrs import field, frozen, evolve, define
from meta_info import MetaInfo
import nameless_lambda
import helpers

Term: TypeAlias = "Term"


@frozen(kw_only=True)
class Term:
    meta_info: MetaInfo = MetaInfo.empty()



@frozen
class Variable(Term):
    __match_args__ = ('name',)
    num: str = field(validator=helpers.not_none)


@frozen
class Abs(Term):
    v: Variable = field(validator=helpers.not_none)
    t: Term = field(validator=helpers.not_none)


@frozen
class App(Term):
    t1: Term = field(validator=helpers.not_none)
    t2: Term = field(validator=helpers.not_none)
