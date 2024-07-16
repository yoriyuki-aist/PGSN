from __future__ import annotations
from typing import TypeAlias
from abc import ABC, abstractmethod
from attrs import field, frozen, evolve
from meta_info import MetaInfo
import helpers

Term: TypeAlias = "Term"
Named: TypeAlias = "Named"
Nameless: TypeAlias = "Nameless"


@frozen(kw_only=True)
class Term(ABC):
    # meta_info is always not empty
    meta_info: MetaInfo = field(default=MetaInfo(), eq=False)


@frozen(kw_only=True)
class Nameless(Term):

    @abstractmethod
    def eval_or_none(self) -> Nameless | None:
        pass

    def eval(self) -> Named:
        return helpers.default(self.eval_or_none(), self)

    @abstractmethod
    def shift(self, num: int, cutoff: int) -> Nameless:
        pass

    @abstractmethod
    def subst_or_none(self, variable: int, term: Nameless) -> Nameless | None:
        pass

    def subst(self, variable:int, term: Nameless) -> Nameless:
        return helpers.default(self.subst_or_none(variable, term), self)

    @abstractmethod
    def recover_name_with_context(self, context: list[str], default_name) -> Named:
        pass

    def recover_name(self) -> Named:
        return self.recover_name_with_context([])


@frozen
class NamelessVariable(Nameless):
    __match_args__ = ('num',)
    num: int = field(validator=helpers.non_negative)

    def eval_or_none(self):
        return None

    def shift(self, d, cutoff):
        if self.num < cutoff:
            return self
        else:
            return evolve(self, num=self.num+d)

    def subst_or_none(self, num, term):
        if self.num == num:
            return term
        else:
            return None

    def recover_name_with_context(self, context, default_name='x'):
        if 0 <= self.num < len(context):
            return NamedVariable(meta_info=self.meta_info,
                                 name=context[self.num])
        else:
            name = helpers.default(self.meta_info.name_info, default_name)
            return NamedVariable(meta_info=self.meta_info,
                                 name=f"{name}_{self.num}")


@frozen
class NamelessAbs(Nameless):
    t: Nameless = field(validator=helpers.not_none)

    def eval_or_none(self):
        reduced = self.t.eval_or_none()
        if reduced is None:
            return None
        else:
            return evolve(self, t=reduced)

    def shift(self, d, c):
        return evolve(self, t=self.t.shift(d, c+1))

    def subst_or_none(self, var, term):
        term_shifted = term.shift(-1, 0)
        substituted = self.t.subst_or_none(var+1, term_shifted)
        if substituted is None:
            return None
        else:
            return evolve(self, t=substituted)

    def recover_name_with_context(self, context, default_name='x'):
        name = helpers.default(self.meta_info.name_info, default_name)
        new_context = [name] + context
        named_term = self.t.recover_name_with_context(context=new_context,
                                                      default_name=default_name)
        named_variable = NamedVariable(name)
        return NamedAbs(meta_info=self.meta_info, v=named_variable, t=named_term)


@frozen
class NamelessApp(Nameless):
    t1: Nameless = field(validator=helpers.not_none)
    t2: Nameless = field(validator=helpers.not_none)

    def eval_or_none(self):
        t1_eval = self.t1.eval_or_none()
        t2_eval = self.t2.eval_or_none()
        t1_prime = helpers.default(t1_eval, self.t1)
        t2_prime = helpers.default(t2_eval, self.t2)
        match t1_prime:
            case NamelessAbs():
                t2_shifted = t2_prime.shift(1, 0)
                t_substituted = t1_prime.subst(0, t2_shifted)
                return t_substituted.shift(-1, 0)
            case BuiltinNameless():
                t = t1_prime.apply_arg(t2_prime)
                if t is None and t1_eval is None and t2_eval is None:
                    return None
                elif t is None:
                    return evolve(self, t1=t1_prime, t2=t2_prime)
                else:
                    return t1_prime.apply_arg(t2_prime)
            case _:
                if t1_eval is None and t2_eval is None:
                    return None
                else:
                    return evolve(self, t1=t1_prime, t2=t2_prime)

    def shift(self, d, c):
        return evolve(self, t1=self.t1.shift(d, c), t2=self.t2.shift(d, c))

    def subst_or_none(self, var, term):
        t1_subst = self.t1.subst(var, term)
        t2_subst = self.t2.subst(var, term)
        if t1_subst is None and t2_subst is None:
            return None
        else:
            return evolve(self, t1=self.t1.subst(var, term), t2=self.t2.subst(var, term))

    def recover_name_with_context(self, context, default_name='x'):
        named_t1 = self.t1.recover_name_with_context(context, default_name)
        named_t2 = self.t2.recover_name_with_context(context, default_name)
        return NamedApp(meta_info=self.meta_info, t1=named_t1, t2=named_t2)


@frozen(kw_only=True)
class Named(Term):

    @classmethod
    def naming_context(cls, names: set[str]) -> list[str]:
        return sorted(list(names))


    @abstractmethod
    def free_variables(self) -> set[str]:
        pass

    @abstractmethod
    def remove_name_with_context(self, naming_context: list[str]) -> Nameless:
        pass

    def my_naming_context(self):
        return self.naming_context(self.free_variables())

    def remove_name(self) -> Nameless:
        return self.remove_name_with_context(self.my_naming_context())


@frozen(order=True)
class NamedVariable(Named):
    name: str = field(validator=helpers.not_none)

    def free_variables(self):
        return {self.name}

    def remove_name_with_context(self, naming_context):
        meta_info = evolve(self.meta_info, name_info=self.name)
        num = naming_context.index(self.name)
        return NamelessVariable(num=num, meta_info=meta_info)


@frozen
class NamedAbs(Named):
    v: NamedVariable = field(validator=helpers.not_none)
    t: Named = field(validator=helpers.not_none)

    def free_variables(self):
        f_vars = self.t.free_variables()
        return f_vars - {self.v.name}

    def remove_name_with_context(self, context):
        meta_info = evolve(self.meta_info, name_info=self.v.name)
        new_context = [self.v.name] + context
        name_less_t = self.t.remove_name_with_context(new_context)
        return NamelessAbs(t=name_less_t, meta_info=meta_info)


@frozen
class NamedApp(Named):
    t1: Named = field(validator=helpers.not_none)
    t2: Named = field(validator=helpers.not_none)

    def free_variables(self):
        return self.t1.free_variables() | self.t2.free_variables()

    def remove_name_with_context(self, context):
        nameless_t1 = self.t1.remove_name_with_context(context)
        nameless_t2 = self.t2.remove_name_with_context(context)
        return NamelessApp(meta_info=self.meta_info,
                           t1=nameless_t1,
                           t2=nameless_t2)


# class for Builtin functions
@frozen
class BuiltinNameless(Nameless):
    name: str = field(validator=helpers.not_none)
    fun = field(validator=helpers.not_none)
    arity: int = field(default=0, validator=helpers.non_negative)
    unlabeled_args: list[Nameless] = field(default=[])
    labels: list[str] = field(default=[], validator=helpers.not_none)
    labeled_args: dict[str, Nameless] = field(default={}, validator=helpers.not_none)

    @fun.validator
    def _check_fun(self, attribute, value):
        assert helpers.fun_with_arity_n(value, 2)

    @unlabeled_args.validator
    def _check_nameless_args(self, attribute, value):
        assert len(value) <= self.arity

    @labeled_args.validator
    def _check_nameless_args(self, attribute, value):
        assert helpers.is_subset(list(value.keys()), self.labels)

    def _reduce(self) -> Nameless:
        return self.fun(self.unlabeled_args, self.labeled_args)

    def _map_args(self, f) -> BuiltinNameless | None:
        unlabeled = [f(arg) for arg in self.unlabeled_args]
        labeled = {label: f(arg) for label, arg in self.labeled_args.items()}
        if all(t is None for t in unlabeled + list(labeled.values())):
            return None
        else:
            return evolve(self, unlabeled_args=unlabeled, labeled_args=labeled)

    def eval_or_none(self) -> Nameless | None:
        return self._map_args(lambda arg: arg.eval_or_none())

    def shift(self, d, cutoff) -> BuiltinNameless:
        return self._map_args(lambda arg: arg.shift(d, cutoff))

    def subst_or_none(self, num, term) -> BuiltinNameless | None:
        return self._map_args(lambda arg: arg.subst_or_none(num, term))

    def recover_name_with_context(self, context, default_name='x') -> BuiltinNamed:
        return BuiltinNamed(name=self.name,
                            fun=self.fun,
                            arity=self.arity,
                            unlabeled_args=self.unlabeled_args,
                            labels=self.labels,
                            labeled_args=self.labeled_args)

    def _can_reduce(self):
        return len(self.unlabeled_args) == self.arity and [self.labeled_args.key()].sort() == self.labels.sort()

    def _apply_arg(self, term: Nameless) -> BuiltinNameless:
        new_list = self.unlabeled_args + [term]
        return evolve(self, unlabeled_args=new_list)

    def apply_arg(self, term: Nameless) -> Nameless:
        t = self._apply_arg(term)
        if t._can_reduce():
            return t._reduce()
        else:
            return t

    def _apply_labeled_arg(self, label: str, term: Nameless) -> BuiltinNameless:
        assert label in self.labels
        assert label not in self.labeled_args.keys()
        new_args = helpers.add_entry(self.labeled_args, label, term)
        return evolve(self, labeled_args=new_args)

    def apply_labeled_arg(self, label: str, term: Nameless) -> Nameless | None:
        t = self._apply_labeled_arg(label, term)
        if t._can_reduce():
            return t._reduce()
        else:
            return t

    def apply_args(self, unlabeled_args: list[Nameless], labeled_args: dict[str, Nameless]) -> Nameless | None:
        assert len(unlabeled_args) == self.arity
        assert [labeled_args.keys()].sort() == self.labels.sort()
        t = self
        for arg in unlabeled_args:
            t = t._apply_arg(arg)
        for label, arg in labeled_args:
            t._apply_labeled_arg(label, arg)
        assert t._can_reduce()
        return t._reduce()


@frozen
class BuiltinNamed(Named):
    name: str = field(validator=helpers.not_none)
    fun: any = field(validator=helpers.not_none),
    arity: int = field(default=0, validator=helpers.non_negative)
    unlabeled_args: list[Named] = field(default=[])
    labels: list[str] = field(default=[], validator=helpers.not_none)
    labeled_args: dict[str, Named] = field(default={}, validator=helpers.not_none)

    def free_variables(self) -> set[str]:
        f_vars_unlabeled = set().union(*{t.free_variables() for t in self.unlabeled_args})
        f_vars_labeled = set().union(*{t.free_variables() for t in self.labeled_args.values()})
        return f_vars_unlabeled.union(f_vars_labeled)

    def remove_name_with_context(self, naming_context: list[str]) -> Nameless:
        nameless_unlabeled_args = [t.remove_name_with_context(naming_context) for t in self.unlabeled_args]
        nameless_labeled_args = {k: t.remove_name_with_context(naming_context) for k, t in self.labeled_args.items()}
        return BuiltinNameless(
            name=self.name,
            fun=self.fun,
            arity=self.arity,
            labels=self.labels,
            unlabeled_args=nameless_unlabeled_args,
            labeled_args=nameless_labeled_args
        )





