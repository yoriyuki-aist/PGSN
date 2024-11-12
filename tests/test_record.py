import meta_info
import pgsn_term
from pgsn_term import lambda_abs_vars, String, Integer, Record
import stdlib
from stdlib import let


def test_record():
    x = pgsn_term.constant('x')
    y = pgsn_term.constant('y')
    z = pgsn_term.constant('z')
    r = stdlib.record({'x': x, 'y': y, 'z': z})
    k1 = stdlib.string('x')
    k2 = stdlib.string('w')
    assert r(k1).eval() == x.eval()
    assert r(k2).eval_or_none() is None


x = pgsn_term.variable('x')
y = pgsn_term.variable('y')
z = pgsn_term.variable('z')
a = pgsn_term.variable('a')
b = pgsn_term.constant('b')
c = pgsn_term.constant('c')
label_1 = stdlib.string('l1')
label_2 = stdlib.string('l2')
r1 = stdlib.record({'l1': a})
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
