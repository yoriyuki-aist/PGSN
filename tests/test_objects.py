import pgsn_term
import object_term
from object_term import method, inherit, instantiate, is_subclass, is_instance
import stdlib
from stdlib import let
from pgsn_term import lambda_abs, lambda_abs_vars


a = stdlib.string('a')
b = stdlib.string('b')
c = stdlib.string('c')
name = stdlib.string('Class')
name1 = stdlib.string('Child')
defaults = stdlib.record({'a': stdlib.boolean(True)})
self = pgsn_term.variable('self')
get_value_term = pgsn_term.lambda_abs(self,
                                        stdlib.if_then_else(self(a))(self(b))(self(c))
                                        )
# attrs1 = inherit(defaults)(record_term.record({'value': get_value_term}))
attrs1 = stdlib.record({'a': stdlib.true, 'value': get_value_term})
cls = object_term.define_class(name)(object_term.base_class)(attrs1)
label_instance = stdlib.string('_instance')
test = stdlib.string('test')


def test_test():
    assert isinstance(get_value_term, pgsn_term.Term)
    assert set(defaults.fully_eval().attributes().keys()) == {'a'}
    assert set(attrs1.fully_eval().attributes().keys()) == {'a', 'value'}


def test_inherit():
    x = pgsn_term.variable('x')
    id = pgsn_term.lambda_abs(x, x)
    zero = stdlib.integer(0)
    one = stdlib.integer(1)
    two = stdlib.integer(2)
    a = stdlib.string('a')
    b = stdlib.string('b')
    c = stdlib.string('c')
    r = stdlib.add_attribute(stdlib.empty_record)(a)(zero)
    r = stdlib.add_attribute(r)(b)(one)
    r1 = stdlib.record({'c': two})
    r2 = object_term.inherit(r)(r1)
    r3 = object_term.inherit(r)(id(r1))
    r4 = stdlib.add_attribute(r1)(b)(zero)
    r5 = object_term.inherit(r)(r4)
    assert r2(a).fully_eval() == zero.fully_eval()
    assert r2(b).fully_eval() == one.fully_eval()
    assert r2(c).fully_eval() == two.fully_eval()
    assert r3(a).fully_eval() == zero.fully_eval()
    assert r3(b).fully_eval() == one.fully_eval()
    assert r3(c).fully_eval() == two.fully_eval()
    assert r5(a).fully_eval() == zero.fully_eval()
    assert r5(b).fully_eval() == zero.fully_eval()
    assert r5(c).fully_eval() == two.fully_eval()


def test_class():
    assert isinstance(cls.fully_eval(), object_term.ClassTerm)
    assert object_term.is_class(cls)
    assert set(cls.fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_parent'}


cls1 = object_term.define_class(name1)(cls)(stdlib.empty_record)


def test_subclass():
    assert isinstance(cls1.fully_eval(), object_term.ClassTerm)
    assert object_term.is_class(cls1)
    assert set(cls1.fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_parent'}
    assert is_subclass(cls)(cls).fully_eval().value
    assert is_subclass(cls1)(cls).fully_eval().value
    assert not is_subclass(object_term.base_class)(cls).fully_eval().value


attrs2 = stdlib.record({'b': b, 'c': c})
attrs3 = stdlib.record({'a': stdlib.boolean(False), 'b': b, 'c': c})
label_value = stdlib.string('value')
obj1 = object_term.instantiate(cls)(stdlib.empty_record)
obj2 = object_term.instantiate(cls)(attrs2)
obj3 = object_term.instantiate(cls)(attrs3)


def test_obj_instance():
    assert isinstance(obj1.fully_eval(), object_term.ObjectTerm)
    assert isinstance(obj2.fully_eval(), object_term.ObjectTerm)
    assert isinstance(obj3.fully_eval(), object_term.ObjectTerm)
    assert is_instance(obj1)(cls).fully_eval().value
    assert not is_instance(obj1)(cls1).fully_eval().value


def test_obj_is_obj():
    assert object_term.is_obj(obj1).fully_eval().value
    assert object_term.is_obj(obj2).fully_eval().value
    assert object_term.is_obj(obj3).fully_eval().value


new_attr = stdlib.add_attribute(stdlib.empty_record)(label_instance)(cls)


def test_obj_labels():
    assert set(new_attr.fully_eval().attributes().keys()) == \
           {'_instance'}
    assert set(stdlib.
               overwrite_record(cls)(new_attr).fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_instance', '_parent'}
    assert set(inherit(cls)(new_attr).fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_instance', '_parent'}
    assert set(obj1.fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_instance', '_parent'}
    assert set(obj2.fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_instance', 'b', 'c', '_parent'}
    assert set(obj3.fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_instance', 'b', 'c', 'a', '_parent'}


def test_obj_values():
    assert obj2(a).fully_eval().value
    assert obj2(b).fully_eval().value == 'b'
    assert obj2(c).fully_eval().value == 'c'
    assert not obj3(a).fully_eval().value
    assert obj3(b).fully_eval().value == 'b'
    assert obj3(c).fully_eval().value == 'c'


def test_obj_methods():
    assert method(obj2)(label_value).fully_eval().value == 'b'
    assert method(obj3)(label_value).fully_eval().value == 'c'


parent = pgsn_term.variable('parent')
attrs = pgsn_term.variable("attrs")
inherit_x = lambda_abs_vars((parent, attrs),
                          stdlib.overwrite_record(parent)(attrs))


def test_obj_labels_x():
    assert set(inherit_x(cls)(new_attr).fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_instance', '_parent'}
