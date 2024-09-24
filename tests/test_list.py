import meta_info
import lambda_term
from list_term import List
from data_term import Integer, String


def test_list():
    x = lambda_term.Constant.nameless('x')
    y = lambda_term.Constant.nameless('y')
    z = lambda_term.Constant.nameless('z')
    ll = List.nameless([x, y, z])
    assert ll.terms == (x, y, z)
