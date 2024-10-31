from attrs import field, frozen
import helpers
from lambda_term import Term, Unary, BuiltinFunction
import lambda_term
from data_term import String
import data_term
from list_term import List
from record_term import Record
import record_term
import stdlib
from lambda_term import lambda_abs, lambda_abs_vars
from stdlib import *

ClassTerm = Record
ObjectTerm = Record


# Special constants
# all labels staring the underscore are reserved for OO systems
_obj = lambda_term.variable("obj")
_parent = lambda_term.variable("parent")
_attrs = lambda_term.variable("attrs")
_x = lambda_term.variable('x')
_y = lambda_term.variable('y')
_self = lambda_term.variable('_self')
_methods = lambda_term.variable("_methods")
_label = lambda_term.variable("_label")
_name = lambda_term.variable("_name")

_label_attrs = data_term.string("_attributes")
_label_methods = data_term.string("_methods")
_label_parent = data_term.string('_parent')
_label_object = data_term.string('_object')
_label_class = data_term.string('_class')
_label_anything = data_term.string('_anything')


_define_obj = lambda_abs(_attrs, stdlib.add_attribute(_attrs)(_label_object)(stdlib.true))

# Attributes
attr = lambda_abs_vars((_obj, _label), _obj(_label))
# Method call
method = lambda_abs_vars((_obj, _label), _obj(_label)(_obj))

# Everything starts here
the_one = _define_obj(stdlib.empty_record)

# Prototyping
inherit = lambda_abs_vars((_parent, _attrs),
                          stdlib.overwrite_record(_parent)(_attrs))

# Class-based OO
# Class
_label_class_name = data_term.string('_class_name')
_class = lambda_term.variable('_class')

define_class = lambda_abs_vars(
    (_name, _parent, _attrs),
    let(_attrs, add_attribute(_attrs)(_label_class_name)(_name),
        inherit(_parent)(_attrs)
        )
    )

is_class = lambda_abs(_class, has_label(_class)(_label_class_name))

base_class = define_class(data_term.string('BaseClass'))(the_one)(stdlib.empty_record)

# Object
_label_instance = data_term.string('_instance')
instantiate = lambda_abs_vars(
    (_class, _attrs),
    (let(
        _attrs, add_attribute(_attrs)(_label_instance)(_class),
        inherit(_class)(_attrs)
    )))
is_obj = lambda_abs(_obj, has_label(_obj)(_label_instance))

_class1 = lambda_term.variable('_class1')
_class2 = lambda_term.variable('_class2')
_is_subclass = lambda_term.variable('_is_subclass')
is_subclass = stdlib.fix(lambda_abs(_is_subclass,
                                    lambda_abs_vars(
                                        (_class1, _class2),
                                        boolean_or
                                        (equal(_class1(_label_class_name))(_class2(_label_class_name)))
                                        (if_then_else
                                         (equal
                                          (_class1(_label_class_name))
                                          (data_term.string('_BaseClass'))
                                          )
                                         (false)
                                         (_is_subclass
                                          (_class1(_label_parent))
                                          (_class2)
                                          )
                                         )
                                    )
                                    )
                         )


_is_instance = lambda_term.variable('_is_instance')
is_instance = lambda_abs_vars(
                             (_obj, _class),
                             is_subclass(_obj(_label_instance))(_class)
)
