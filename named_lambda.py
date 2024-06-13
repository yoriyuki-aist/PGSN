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

    @classmethod
    def naming_context(cls, vars: set[Variable]) -> list[Variable]:
        return sorted(vars)

    def free_variables(self) -> set[Variable]:
        pass

    def remove_name_with_context(self, naming_context: list[Variable]) -> nameless_lambda.Term:
        pass

    def my_naming_context(self):
        return self.naming_context(self.free_variables())

    def remove_name(self) -> nameless_lambda.Term:
        return self.remove_name_with_context(self.my_naming_context())


@frozen(order=True)
class Variable(Term):
    name: str = field(validator=helpers.not_none)

    def free_variables(self):
        return {self}

    def remove_name_with_context(self, naming_context):
        meta_info = evolve(self.meta_info, name_info=self.name)
        num = naming_context.index(self)
        return nameless_lambda.Variable(num=num, meta_info=meta_info)


@frozen
class Abs(Term):
    v: Variable = field(validator=helpers.not_none)
    t: Term = field(validator=helpers.not_none)

    def free_variables(self):
        fvars = self.t.free_variables()
        return fvars - {self.v}

    def remove_name_with_context(self, context):
        meta_info = evolve(self.meta_info, name_info=self.v.name)
        new_context = [self.v] + context
        name_less_t = self.t.remove_name_with_context(new_context)
        return nameless_lambda.Abs(t=name_less_t, meta_info=meta_info)



@frozen
class App(Term):
    t1: Term = field(validator=helpers.not_none)
    t2: Term = field(validator=helpers.not_none)

    def free_variables(self):
        return self.t1.free_variables() + self.t2.free_variables()

    def remove_name_with_context(self, context):
        nameless_t1 = self.t1.remove_name_with_context(context)
        nameless_t2 = self.t2.remove_name_with_context(context)
        return nameless_lambda.App(meta_info=self.meta_info,
                                   t1=nameless_t1,
                                   t2=nameless_t2)


