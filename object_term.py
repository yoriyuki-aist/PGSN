from __future__ import annotations
from typing import TypeAlias
from attrs import field, frozen, evolve
import helpers
from lambda_term import Term, Unary, BuiltinFunction
from data_term import String
from list_term import List
from record_term import Record

ObjectTerm: TypeAlias = "ObjectTerm"
ClassTerm: TypeAlias = "ClassTerm"


# class_term(attribute) -> object_term
@frozen
class ClassTerm(Unary):
    name: str | None = field()
    super_class: ClassTerm = field(default=None)
    # attribute names and their defaults.  None means no default
    _attributes: dict[str, Term | None] = field(default={}, validator=helpers.not_none)
    _methods: dict[str, Term] = field(default={})

    def __attr_post_init__(self):
        assert self.super_class is not None
        assert all((t is None or t == self.is_named for _, t in self._attributes.items()))
        assert all((t == self.is_named for _, t in self._methods.items()))
        assert all((k not in self._methods for k, _ in self._attributes.items()))
        assert all((k not in self._methods for k, _ in self._methods.items()))

    @classmethod
    def build(cls,
              is_named: bool,
              super_class: ClassTerm | None,
              attributes: dict[str, Term | None],
              methods: dict[str, Term],
              name: str,
              ):
        return cls(name=name,
                   is_named=is_named,
                   super_class=super_class,
                   attributes=attributes.copy(),
                   methods=methods.copy())

    def attributes(self):
        return self._attributes.copy()

    def methods(self):
        return self._methods.copy()

    # def evolve(self, is_named: bool | None = None,
    #            name: str | None = None,
    #            super_class: ClassTerm | None = None,
    #            attributes: dict[str, Term | None] | None =None,
    #            methods: dict[str, Term] = None):
    #     if is_named is None:
    #         is_named = self.is_named
    #     if super_class is None:
    #         super_class = self.super_class
    #     if attributes is None:
    #         attributes = self._attributes
    #     if methods is None:
    #         methods = self._methods
    #     return evolve(self,
    #                   is_named=is_named,
    #                   name=name,
    #                   super_class=super_class,
    #                   attributes=attributes.copy(),
    #                   methods=methods.copy())

    def _applicable(self, arg: Term):
        if not isinstance(arg, Record):
            return False
        r = arg.attributes()
        for k, t in self._attributes.items():
            if k not in r and t is None:
                return False
        return True

    def _apply_arg(self, arg: Record):
        return self.instantiate(attrs=arg.attributes())

    def instantiate(self, attrs: dict[str, Term]) -> ObjectTerm:
        if self.super_class is not None:
            p = self.super_class.instantiate(attrs)
        else:
            p = None
        for k, t in self._attributes.items():
            if k not in attrs and self._attributes[k] is not None:
                attrs[k] = self._attributes[k]
        return ObjectTerm.build(is_named=self.is_named,
                                parent=p,
                                attributes=attrs,
                                instance=self)

    def is_subclass(self, cls: ClassTerm):
        if self == cls:
            return True
        if self.super_class is None:
            return False
        return self.super_class.is_subclass(cls)


base_class = ClassTerm.build(is_named=True,
                             super_class=None,
                             attributes={},
                             methods={},
                             name='BaseClass')


# define_class(name)(super)(attribute_names)(attribute_default)(methods)
@frozen
class DefineClass(BuiltinFunction):
    arity = 5
    name = 'DefineClass'

    def _applicable_args(self, args:tuple[Term, ...]):
        # Name
        if not isinstance(args[0], String):
            return False
        if not isinstance(args[1], ClassTerm):
            return False
        # attributes
        if not isinstance(args[2], List):
            return False
        # key must be a string
        for value in args[2].terms:
            if not isinstance(value, String):
                return False
        # default values
        if not isinstance(args[3], Record):
            return False
        # methods
        return isinstance(args[4], Record)

    def _apply_args(self, args:tuple[Term, ...]) -> ClassTerm:
        name = args[0].value
        super_class = args[1]
        attrs = {t.value: None for t in args[2].terms}
        for k, t in args[3].attributes().items():
            if k in attrs:
                attrs[k] = t
        methods = args[4].attributes()
        return ClassTerm.build(is_named=self.is_named,
                               name=name,
                               super_class=super_class,
                               attributes=attrs,
                               methods=methods
                               )


define_class = DefineClass.named()


@frozen
class ObjectTerm(Unary):
    # Hack: syntactically, instance is an optional argument but must be specified otherwise
    # the runtime error occurs.
    parent: ObjectTerm | None
    instance: ClassTerm = field(default=None, validator=helpers.not_none)
    _attributes: dict[str, Term] = field(default={})

    def __attr_post_init__(self):
        assert self.instance is not None
        assert all((t == self.is_named for _, t in self._attributes.items()))
        assert all((t == self.is_named for _, t in self.instance.methods().items()))
        assert self._attributes.keys() == self.instance.attributes().keys()

    @classmethod
    def build(cls, is_named: bool,
              instance: ClassTerm,
              attributes: dict[str, Term],
              parent: ObjectTerm | None = None):
        attrs = attributes.copy()
        return cls(is_named=is_named,
                   instance=instance,
                   attributes=attrs,
                   parent=parent)

    # def evolve(self, is_named: bool | None = None,
    #            attributes: dict[str, Term] | None =None,
    #            methods: dict[str, Term] = None):
    #     if is_named is None:
    #         is_named = self.is_named
    #     if attributes is None:
    #         attributes = self._attributes
    #     return evolve(self, is_named=is_named, attributes=attributes.copy())
    def _applicable(self, arg:Term):
        if not isinstance(arg, String):
            return False
        key = arg.value
        if key in self._attributes:
            return True
        if key in self.instance.methods().keys():
            return True
        if self.parent is not None:
            return self.parent.applicable_args((arg,))
        else:
            return False

    def _apply_arg(self, arg: String):
        key = arg.value
        if key in self._attributes:
            return self._attributes[key]
        if key in self.instance.methods():
            return self.instance.methods()[key](self)
        if self.parent is not None:
            return self.parent.apply_args((arg,))
        assert False

    def is_instance(self, cls: ClassTerm):
        if cls == self.instance:
            return True
        if self.parent is not None:
            return self.parent.is_instance(cls)
        else:
            return False

