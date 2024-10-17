import list_term
import lambda_term
import data_term
import record_term
import object_term
import stdlib

a = data_term.string('a')
b = data_term.string('b')
c = data_term.string('c')
name = data_term.string('Class')
name1 = data_term.string('Child')
attrs = (a, b, c)
attrs_term = list_term.List.named(terms=attrs)
defaults = record_term.record({'a': data_term.boolean(True)})
self = lambda_term.variable('self')
get_value_term = lambda_term.lambda_abs(self,
                                        stdlib.if_then_else(self(a))(self(b))(self(c))
                                        )
methods = record_term.record({'value': get_value_term})
cls = object_term.define_class(name)(object_term.base_class)(attrs_term)(defaults)(methods)
attrs1 = record_term.record({})
attrs2 = record_term.record({'b': b, 'c': c})
attrs3 = record_term.record({'a': data_term.boolean(False), 'b': b, 'c': c})
obj1 = cls(attrs1)
obj2 = cls(attrs2)
obj3 = cls(attrs3)


def test_class():
    assert not isinstance(obj1.fully_eval(), object_term.ObjectTerm)
    assert isinstance(obj2.fully_eval(), object_term.ObjectTerm)
    assert isinstance(obj3.fully_eval(), object_term.ObjectTerm)


value = data_term.string('value')


def test_obj():
    assert obj2(a).fully_eval().value
    assert obj2(b).fully_eval().value == 'b'
    assert obj2(c).fully_eval().value == 'c'
    assert obj2(value).fully_eval().value == 'b'

    assert not obj3(a).fully_eval().value
    assert obj3(b).fully_eval().value == 'b'
    assert obj3(c).fully_eval().value == 'c'
    assert obj3(value).fully_eval().value == 'c'
