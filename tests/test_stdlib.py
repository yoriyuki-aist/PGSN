import meta_info
from lambda_term import App, Constant
import list_term
import lambda_term
from data_term import String, Integer
from list_term import List
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
    assert stdlib.index(t2)(Integer.named(0)).fully_eval() == d.fully_eval()
    assert stdlib.index(t2)(Integer.named(1)).fully_eval() == c.fully_eval()
    assert t3.fully_eval() == t.fully_eval()


# def test_fold():
