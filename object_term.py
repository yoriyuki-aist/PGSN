from __future__ import annotations
from typing import TypeAlias
from attrs import field, frozen, evolve
import helpers
import lambda_term
from lambda_term import Term, Unary, BuiltinFunction
from data_term import String
from record_term import Record

ObjectTerm: TypeAlias = "ObjectTerm"
ClassTerm: TypeAlias = "ClassTerm"


# hack
base_class = None


@frozen
class ObjectTerm(Unary):
    instance: ClassTerm = field(default=base_class, validator=helpers.not_none)
    _attributes: dict[str, Term] = field(default={})
    _methods: dict[str, Term] = field(default={})

    def __attr_post_init__(self):
        assert all((t == self.is_named for _, t in self._attributes.items()))
        assert all((t == self.is_named for _, t in self._methods.items()))
        assert all((k not in self._methods for k, _ in self._attributes.items()))
        assert all((k not in self._methods for k, _ in self._methods.items()))

    @classmethod
    def build(cls, is_named: bool, attributes: dict[str, Term], methods: dict[str, Term]):
        return cls(is_named=is_named, attributes=attributes.copy(), methods=methods.copy())

    def evolve(self, is_named: bool | None = None,
               attributes: dict[str, Term] | None =None,
               methods: dict[str, Term] = None):
        if is_named is None:
            is_named = self.is_named
        if attributes is None:
            attributes = self._attributes
        if methods is None:
            methods = self._methods
        return evolve(self, is_named=is_named, attributes=attributes.copy(), methods=methods.copy())

    def _applicable(self, arg:Term):
        return isinstance(arg, String) and (arg.value in self._attributes or arg.value in self._methods)

    def _apply_arg(self, arg: String):
        label = arg.value
        if label in self._attributes:
            return self._attributes[label]
        if label in self._methods:
            return self._methods[label](self)

    def is_instance(self, cls: ClassTerm):
        return self.instance.is_subclass(cls)

    def has_type(self, cls):
        return set(self._attributes.keys()).issubset(cls.attributes().keys) and \
            set(self._methods.keys()).issubset(cls.methods().keys)


@frozen
class ClassTerm(Unary):
    super: ClassTerm = field()
    # attribute names and their defaults.  None means no default
    _attributes: dict[str, Term | None] = field(default={}, validator=helpers.not_none)
    _methods: dict[str, Term] = field(default={})

    def __attr_post_init__(self):
        assert all((t is None or t == self.is_named for _, t in self._attributes.items()))
        assert all((t == self.is_named for _, t in self._methods.items()))
        assert all((k not in self._methods for k, _ in self._attributes.items()))
        assert all((k not in self._methods for k, _ in self._methods.items()))

    @classmethod
    def built(cls, is_named: bool, attributes: dict[str, Term | None], methods: dict[str, Term]):
        return cls(is_named=is_named, attributes=attributes.copy(), methods=methods.copy())

    def attributes(self):
        return self._attributes.copy()

    def methods(self):
        return self._methods.copy()

    def evolve(self, is_named: bool | None = None,
               attributes: dict[str, Term | None] | None =None,
               methods: dict[str, Term] = None):
        if is_named is None:
            is_named = self.is_named
        if attributes is None:
            attributes = self._attributes
        if methods is None:
            methods = self._methods
        return evolve(self, is_named=is_named, attributes=attributes.copy(), methods=methods.copy())

    def _applicable(self, arg: Term):
        if not isinstance(arg, Record):
            return False
        r = arg.terms()
        if not all((k in self._attributes for k, _ in arg.terms().items())):
            return False
        for k, t in self._attributes.items():
            if not (k in r or t is not None):
                return False
        return True

    def _apply_arg(self, arg: Record):
        r = arg.terms()
        for k, t in self._attributes.items():
            if k not in r and self._attributes[k] is not None:
                r[k] = self._attributes[k]
        return ObjectTerm.build(is_named=self.is_named,
                                attributes=r,
                                methods=self._methods)

    def instantiate(self, arg:Record):
        return self.apply_args((arg,))

    def is_subclass(self, cls: ClassTerm):
        if self == cls:
            return True
        if self.super is None:
            return False
        return self.super.is_subclass(cls)


