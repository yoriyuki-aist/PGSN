
import meta_info
import lambda_term
import stdlib
from lambda_term import List


def test_list():
    x = lambda_term.constant('x')
    y = lambda_term.constant('y')
    z = lambda_term.constant('z')
    ll = List.named(terms=(x, y, z))
    assert ll.terms == (x, y, z)
    i = stdlib.integer(1)
    assert ll(i).eval().name == 'y'