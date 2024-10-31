import meta_info
import lambda_term
from lambda_term import lambda_abs_vars
from record_term import Record
import record_term
from data_term import Integer, String
import data_term
import stdlib
from stdlib import let


def test_record():
    x = lambda_term.constant('x')
    y = lambda_term.constant('y')
    z = lambda_term.constant('z')
    r = record_term.record({'x': x, 'y': y, 'z': z})
    k1 = data_term.string('x')
    k2 = data_term.string('w')
    assert r(k1).eval() == x.eval()
    assert r(k2).eval_or_none() is None


x = lambda_term.variable('x')
y = lambda_term.variable('y')
z = lambda_term.variable('z')
a = lambda_term.variable('a')
b = lambda_term.constant('b')
c = lambda_term.constant('c')
label_1 = data_term.string('l1')
label_2 = data_term.string('l2')
r1 = record_term.record({'l1': a})
r2 = stdlib.add_attribute(stdlib.empty_record)(label_2)(r1)
r3 = stdlib.overwrite_record(r1)(r2)
def test_self_reference1():
    assert set(r3.fully_eval().attributes().keys()) == {'l1', 'l2'}


def test_self_reference2():
    f = lambda_abs_vars((x, y),
                        let(
                            y, stdlib.add_attribute(y)(label_2)(x),
                            stdlib.overwrite_record(x)(y)
                        )
                        )
    assert set(f(r1)(r2).fully_eval().attributes().keys()) == {'l1', 'l2'}


def test_self_reference3():
    f1 = lambda_abs_vars((x, y),
                        stdlib.overwrite_record(x)(stdlib.add_attribute(y)(label_2)(x))
                    )
    assert set(f1(r1)(r2).fully_eval().attributes().keys()) == {'l1', 'l2'}


def test_self_reference4():
    r = stdlib.overwrite_record(r1)(stdlib.add_attribute(r2)(label_2)(r1),)
    assert set(r.fully_eval().attributes().keys()) == {'l1', 'l2'}
