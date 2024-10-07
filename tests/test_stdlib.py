import list_term
import lambda_term
import data_term
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
