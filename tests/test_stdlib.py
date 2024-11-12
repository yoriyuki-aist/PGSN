import lambda_term
import stdlib
from stdlib import lambda_abs, lambda_abs_vars, lambda_abs_keywords, plus, let


def test_list():
    c = lambda_term.constant('c')
    d = lambda_term.constant('d')
    t = stdlib.cons(c)(stdlib.empty)
    t1 = stdlib.head(t)
    t2 = stdlib.cons(d)(t)
    t3 = stdlib.tail(t2)
    assert t.fully_eval().terms[0] == c.fully_eval()
    assert t1.fully_eval() == c.fully_eval()
    assert t2.fully_eval().terms == (d.remove_name(), c.remove_name())
    assert t3.fully_eval() == t.fully_eval()
    assert stdlib.index(t2)(stdlib.integer(0)).fully_eval() == d.fully_eval()
    assert stdlib.index(t2)(stdlib.integer(1)).fully_eval() == c.fully_eval()
    assert t3.fully_eval() == t.fully_eval()


def test_integer():
    i1 = stdlib.integer(1)
    i2 = stdlib.integer(1)
    i = stdlib.plus(i1)(i2)
    assert i.fully_eval().value == 2


def test_fold():
    i1 = stdlib.integer(1)
    i2 = stdlib.integer(1)
    ll = stdlib.cons(i1)(stdlib.cons(i2)(stdlib.empty))
    i = stdlib.integer_sum(ll)
    assert i.fully_eval().value == 2


def test_map():
    i1 = stdlib.integer(1)
    i2 = stdlib.integer(2)
    ll = stdlib.cons(i1)(stdlib.cons(i2)(stdlib.empty))
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
    default = stdlib.integer(1)
    defaults = stdlib.record({'b': default}, )
    f = lambda_abs_vars((x, y), lambda_abs_keywords(('a', 'b'), defaults, stdlib.plus(x)(b)))
    f1 = lambda_abs(x, lambda_abs_keywords(('a',), stdlib.empty_record, stdlib.plus(x)(a)))
    zero = stdlib.integer(0)
    one = stdlib.integer(1)
    two = stdlib.integer(2)
    three = stdlib.integer(2)
    r = stdlib.record({'a': zero})
    assert f1(one)(r).fully_eval().value == 1
    assert f(one)(two)(r).fully_eval().value == 2
    r1 = stdlib.record({'a': zero, 'b': zero})
    assert f(one)(two)(r1).fully_eval().value == 1
    r2 = stdlib.record({})
    assert isinstance(f1(one)(two)(r2).fully_eval(), lambda_term.App)


def test_let():
    x = lambda_term.variable('x')
    identity = lambda_term.lambda_abs(x, x)
    t = x(x)
    t1 = stdlib.let(x, identity, t)
    assert t1.fully_eval() == identity.fully_eval()


def test_let2():
    x = lambda_term.variable('x')
    y = lambda_term.variable('y')
    one = stdlib.integer(1)
    two = stdlib.integer(2)
    t = lambda_abs_vars((x, y),
                        (lambda_abs(x, plus(x)(y))(plus(x)(x)))
                        )
    assert t(one)(two).fully_eval().value == 4
    t1 = lambda_abs_vars((x, y),
                         let(x, plus(x)(x),
                             plus(x)(y)
                             )
                         )
    assert t1(one)(two).fully_eval().value == 4


def test_bool():
    c = lambda_term.constant('c')
    d = lambda_term.constant('d')
    true = stdlib.boolean(True)
    false = stdlib.boolean(False)
    assert stdlib.if_then_else(true)(c)(d).fully_eval() == c.fully_eval()
    assert stdlib.if_then_else(false)(c)(d).fully_eval() == d.fully_eval()
    assert stdlib.guard(true)(c).fully_eval() == c.fully_eval()
    assert stdlib.guard(false)(c).fully_eval() != c.fully_eval()


def test_equal():
    s1 = stdlib.string('s1')
    s2 = stdlib.string('s2')
    assert stdlib.equal(s1)(s1).fully_eval().value
    assert not stdlib.equal(s1)(s2).fully_eval().value


def test_record():
    zero = stdlib.integer(0)
    one = stdlib.integer(1)
    two = stdlib.integer(2)
    a = stdlib.string('a')
    b = stdlib.string('b')
    c = stdlib.string('c')
    r = stdlib.add_attribute(stdlib.empty_record)(a)(zero)
    r = stdlib.add_attribute(r)(b)(one)
    assert isinstance(r.fully_eval(), lambda_term.Record)
    assert r(b).fully_eval().value == 1
    assert stdlib.has_label(r)(b).fully_eval().value
    assert not stdlib.has_label(r)(c).fully_eval().value
    assert stdlib.has_label(stdlib.remove_attribute(r)(b))(a).fully_eval().value
    assert not stdlib.has_label(stdlib.remove_attribute(r)(b))(b).fully_eval().value
    assert stdlib.list_labels(r).fully_eval() == lambda_term.List.named(terms=(a, b)).fully_eval()
    r1 = stdlib.record({'c': two})
    assert stdlib.overwrite_record(r)(r1)(a).fully_eval().value == 0
    assert stdlib.overwrite_record(r)(r1)(c).fully_eval().value == 2
    r2 = stdlib.record({'b': two})
    assert stdlib.overwrite_record(r)(r2)(b).fully_eval().value == 2


class Id(lambda_term.Unary):
    arity = 1

    def _applicable(self, args):
        return True

    def _apply_arg(self, arg):
        return arg


def test_lambda_term_nested2():
    id_f = Id.named()
    x = lambda_term.variable('x')
    y = lambda_term.variable('y')
    z = lambda_term.variable('z')
    a = lambda_term.constant('a')
    b = lambda_term.constant('b')
    label = stdlib.string('ll')
    t = lambda_term.lambda_abs_vars(
        (x, y),
        stdlib.let(x, id_f(x), id_f(x)))
    assert t(a)(b).fully_eval() == a.fully_eval()
    t2 = lambda_abs_vars((x, y), t(x)(y))
    assert t2(a)(b).fully_eval() == a.fully_eval()
    t3 = lambda_term.lambda_abs_vars(
        (x, y),
        stdlib.let(
            x, stdlib.add_attribute(stdlib.empty_record)(label)(x),
            stdlib.overwrite_record(x)(y)
        )
    )
    r = stdlib.record({'a': a})
    label_a = stdlib.string('a')
    assert t3(stdlib.empty_record)(r)(label_a).fully_eval() == a.fully_eval()
    assert stdlib.has_label(t3(stdlib.empty_record)(r))(label).fully_eval()
    assert t3(stdlib.empty_record)(r)(label).fully_eval() == stdlib.empty_record.fully_eval()


x = lambda_term.variable('x')
y = lambda_term.variable('y')
z = lambda_term.variable('z')
f = lambda_term.lambda_abs(x, x)
label_a = stdlib.string('a')
label_f = stdlib.string('f')
r1 = stdlib.record({'a': stdlib.true})
r2 = stdlib.record({'f': f})
r3 = stdlib.add_attribute(stdlib.empty_record)(label_a)(stdlib.true)
r4 = stdlib.add_attribute(stdlib.empty_record)(label_f)(f)


def test_overwrite_record_fun():
    assert set(stdlib.overwrite_record(r1)(stdlib.empty_record).\
        fully_eval().attributes().keys()) == {'a'}
    assert set(stdlib.overwrite_record(r2)(stdlib.empty_record).\
        fully_eval().attributes().keys()) == {'f'}


eta = lambda_term.lambda_abs_vars((y, z), stdlib.overwrite_record(y)(z))


def test_overwrite_record_eta():
    assert set(eta(r1)(stdlib.empty_record). \
               fully_eval().attributes().keys()) == {'a'}
    assert set(eta(r2)(stdlib.empty_record). \
               fully_eval().attributes().keys()) == {'f'}


def test_add_attribute_record_fun():
    assert set(r3.fully_eval().attributes().keys()) == {'a'}
    assert set(r4.fully_eval().attributes().keys()) == {'f'}
    assert set(stdlib.add_attribute(r3)(label_a)(stdlib.true). \
               fully_eval().attributes().keys()) == {'a'}
    assert set(stdlib.add_attribute(r4)(label_f)(f). \
               fully_eval().attributes().keys()) == {'f'}
