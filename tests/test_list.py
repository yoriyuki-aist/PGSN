
import meta_info
import pgsn_term
import stdlib
from pgsn_term import List


def test_list():
    x = pgsn_term.constant('x')
    y = pgsn_term.constant('y')
    z = pgsn_term.constant('z')
    ll = List.named(terms=(x, y, z))
    assert ll.terms == (x, y, z)
    i = stdlib.integer(1)
    assert ll(i).eval().name == 'y'