import list_term
import lambda_term
import data_term
import record_term
import object_term
from object_term import method, inherit, instantiate
import stdlib
from stdlib import let
from lambda_term import lambda_abs, lambda_abs_vars


a = data_term.string('a')
b = data_term.string('b')
c = data_term.string('c')
name = data_term.string('Class')
name1 = data_term.string('Child')
defaults = record_term.record({'a': data_term.boolean(True)})
self = lambda_term.variable('self')
get_value_term = lambda_term.lambda_abs(self,
                                        stdlib.if_then_else(self(a))(self(b))(self(c))
                                        )
# attrs1 = inherit(defaults)(record_term.record({'value': get_value_term}))
attrs1 = record_term.record({'a': stdlib.true, 'value': get_value_term})
cls = object_term.define_class(name)(object_term.base_class)(attrs1)
label_instance = data_term.string('_instance')
test = data_term.string('test')


def test_test():
    assert isinstance(get_value_term, lambda_term.Term)
    assert set(defaults.fully_eval().attributes().keys()) == {'a'}
    assert set(attrs1.fully_eval().attributes().keys()) == {'a', 'value'}


def test_inherit():
    x = lambda_term.variable('x')
    id = lambda_term.lambda_abs(x, x)
    zero = data_term.integer(0)
    one = data_term.integer(1)
    two = data_term.integer(2)
    a = data_term.string('a')
    b = data_term.string('b')
    c = data_term.string('c')
    r = stdlib.add_attribute(stdlib.empty_record)(a)(zero)
    r = stdlib.add_attribute(r)(b)(one)
    r1 = record_term.record({'c': two})
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
           {'a', 'value', '_object', '_class_name'}


attrs2 = record_term.record({'b': b, 'c': c})
attrs3 = record_term.record({'a': data_term.boolean(False), 'b': b, 'c': c})
label_value = data_term.string('value')
obj1 = object_term.instantiate(cls)(stdlib.empty_record)
obj2 = object_term.instantiate(cls)(attrs2)
obj3 = object_term.instantiate(cls)(attrs3)


def test_obj_instance():
    assert isinstance(obj1.fully_eval(), object_term.ObjectTerm)
    assert isinstance(obj2.fully_eval(), object_term.ObjectTerm)
    assert isinstance(obj3.fully_eval(), object_term.ObjectTerm)


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
           {'a', 'value', '_object', '_class_name', '_instance'}
    assert set(inherit(cls)(new_attr).fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_instance'}
    assert set(obj1.fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_instance'}
    assert set(obj2.fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_instance', 'b', 'c'}
    assert set(obj3.fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_instance', 'b', 'c', 'a'}


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


parent = lambda_term.variable('parent')
attrs = lambda_term.variable("attrs")
inherit_x = lambda_abs_vars((parent, attrs),
                          stdlib.overwrite_record(parent)(attrs))


def test_obj_labels_x():
    assert set(inherit_x(cls)(new_attr).fully_eval().attributes().keys()) == \
           {'a', 'value', '_object', '_class_name', '_instance'}
