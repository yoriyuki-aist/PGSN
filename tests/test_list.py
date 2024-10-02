
import meta_info
import lambda_term
from list_term import List
from data_term import Integer, String
import data_term


def test_list():
    x = lambda_term.constant('x')
    y = lambda_term.constant('y')
    z = lambda_term.constant('z')
    ll = List.named(terms=(x, y, z))
    assert ll.terms == (x, y, z)
    i = data_term.integer(1)
    assert ll(i).eval().name == 'y'