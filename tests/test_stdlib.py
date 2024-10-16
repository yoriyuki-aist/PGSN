import list_term
import lambda_term
import data_term
import record_term
import stdlib


def test_list():
    c = lambda_term.constant('c')
    d = lambda_term.constant('d')
    t = stdlib.cons(c)(list_term.empty)
    t1 = stdlib.head(t)
    t2 = stdlib.cons(d)(t)
    t3 = stdlib.tail(t2)
    assert t.fully_eval().terms[0] == c.fully_eval()
    assert t1.fully_eval() == c.fully_eval()
    assert t2.fully_eval().terms == (d.remove_name(), c.remove_name())
    assert t3.fully_eval() == t.fully_eval()
    assert stdlib.index(t2)(data_term.integer(0)).fully_eval() == d.fully_eval()
    assert stdlib.index(t2)(data_term.integer(1)).fully_eval() == c.fully_eval()
    assert t3.fully_eval() == t.fully_eval()


def test_integer():
    i1 = data_term.integer(1)
    i2 = data_term.integer(1)
    i = stdlib.plus(i1)(i2)
    assert i.fully_eval().value == 2


def test_fold():
    i1 = data_term.integer(1)
    i2 = data_term.integer(1)
    ll = stdlib.cons(i1)(stdlib.cons(i2)(list_term.empty))
    i = stdlib.integer_sum(ll)
    assert i.fully_eval().value == 2


def test_map():
    i1 = data_term.integer(1)
    i2 = data_term.integer(2)
    ll = stdlib.cons(i1)(stdlib.cons(i2)(list_term.empty))
    plus_one = stdlib.plus(i1)
    ll_1 = stdlib.map_term(plus_one)(ll)
    assert len(ll_1.fully_eval().terms) == 2
    assert ll_1.fully_eval().terms[0].value == 2
    assert ll_1.fully_eval().terms[1].value == 3


def test_multi_arg_function():
    x = lambda_term.variable('x')
    y = lambda_term.variable('y')
    a = lambda_term.variable('a')
    b = lambda_term.variable('b')
    default = data_term.integer(1)
    f = stdlib.multi_arg_function((x, y), {'a': None, 'b': default},
                                  stdlib.plus(x)(b)
                                  )
    f1 = stdlib.multi_arg_function((x,), {'a': None}, stdlib.plus(x)(a))
    zero = data_term.integer(0)
    one = data_term.integer(1)
    two = data_term.integer(2)
    three = data_term.integer(2)
    r = record_term.record({'a': zero})
    assert f1(one)(r).fully_eval().value == 1
    assert f(one)(two)(r).fully_eval().value == 2
    r1 = record_term.record({'a': zero, 'b': zero})
    assert f(one)(two)(r1).fully_eval().value == 1
    r2 = record_term.record({})
    assert isinstance(f(one)(two)(r2).fully_eval(), lambda_term.App)


def test_let():
    x = lambda_term.variable('x')
    identity = lambda_term.lambda_abs(x, x)
    t = x(x)
    t1 = stdlib.let(x, identity, t)
    assert t1.fully_eval() == identity.fully_eval()


def test_bool():
    c = lambda_term.constant('c')
    d = lambda_term.constant('d')
    true = data_term.boolean(True)
    false = data_term.boolean(False)
    assert stdlib.if_then_else(true)(c)(d).fully_eval() == c.fully_eval()
    assert stdlib.if_then_else(false)(c)(d).fully_eval() == d.fully_eval()
    assert stdlib.guard(true)(c).fully_eval() == c.fully_eval()
    assert stdlib.guard(false)(c).fully_eval() != c.fully_eval()

