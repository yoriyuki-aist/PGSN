import meta_info
import pgsn_term
from pgsn_term import *
import stdlib
from stdlib import let
# import string_term
# import list_term
# import record_term


def test_meta_info():
    info = meta_info.MetaInfo()
    assert info is not None


def test_var():
    info = meta_info.MetaInfo(name_info='x')
    var_x = pgsn_term.Variable.named(name='x', meta_info=info)
    nameless_x = var_x.remove_name()
    assert nameless_x.meta_info.name_info == 'x'


def test_pgsn_term_id():
    x = pgsn_term.variable('x')
    id_f = pgsn_term.lambda_abs(x, x)
    t = id_f(id_f)
    assert t.eval() == id_f.eval()


def test_pgsn_term_const():
    c = pgsn_term.constant('c')
    x = pgsn_term.variable('x')
    id_f = pgsn_term.lambda_abs(x, c)
    t = id_f(c)
    assert t.eval() == c.eval()


def test_pgsn_term_nested():
    x = pgsn_term.variable('x')
    y = pgsn_term.variable('y')
    z = pgsn_term.variable('z')
    c = pgsn_term.constant('c')
    d = pgsn_term.constant('d')
    p1 = pgsn_term.lambda_abs(x, pgsn_term.lambda_abs(y, x))
    t = pgsn_term.lambda_abs(y, pgsn_term.lambda_abs(x, p1(x)(y)))
    assert t(c)(d).fully_eval() == d.fully_eval()


def test_pgsn_term_higher_order():
    x = pgsn_term.variable('x')
    y = pgsn_term.variable('y')
    z = pgsn_term.variable('z')
    c = pgsn_term.constant('c')
    d = pgsn_term.constant('d')
    p1 = pgsn_term.lambda_abs(x, pgsn_term.lambda_abs(y, x))
    assert p1(c)(d).fully_eval() == c.fully_eval()
    t = pgsn_term.lambda_abs(y, y(c)(d))(p1)
    assert t.fully_eval() == c.fully_eval()


class Id(pgsn_term.Unary):
    arity = 1

    def _applicable(self, args):
        return True

    def _apply_arg(self, arg):
        return arg


def test_builtin():
    id_f = Id.named().eval()
    c = pgsn_term.constant('c').eval()
    assert id_f.applicable_args((c,))
    assert id_f.apply_args((c,)) == (c, tuple())
    assert id_f(c).eval() == c


def test_higher_order2():
    x = pgsn_term.variable('x')
    y = pgsn_term.variable('y')
    f = pgsn_term.variable('f')
    a = pgsn_term.constant('a')
    id = lambda_abs(x, x)
    g = pgsn_term.lambda_abs_vars((f, y), f(y))
    assert g(id)(a).fully_eval() == a.fully_eval()
    h = pgsn_term.lambda_abs(f, f(a))
    assert h(id).fully_eval() == a.fully_eval()


def test_eta_expansion():
    x = pgsn_term.variable('x')
    y = pgsn_term.variable('y')
    one = stdlib.integer(1)
    two = stdlib.integer(2)
    assert stdlib.plus(one)(two).fully_eval().value == 3
    f = lambda_abs_vars((x, y), stdlib.plus(x)(y))
    assert f(one)(two).fully_eval().value == 3


def test_self_reference():
    x = pgsn_term.variable('x')
    y = pgsn_term.variable('y')
    one = stdlib.integer(1)
    two = stdlib.integer(2)
    f = lambda_abs_vars((x, y),
                        let(
                            x, stdlib.plus(x)(y),
                            stdlib.plus(x)(y)
                        ))
    assert f(one)(two).fully_eval().value == 5

