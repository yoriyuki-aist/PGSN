import meta_info
import lambda_term
from list_term import List
from data_term import Integer, String


def test_list():
    x = lambda_term.Constant.nameless('x')
    y = lambda_term.Constant.nameless('y')
    z = lambda_term.Constant.nameless('z')
    ll = List.nameless([x, y, z])
    assert ll(Integer.nameless(0)).eval() == x
    assert ll(Integer.nameless(1)).eval() == y
    assert ll(Integer.nameless(2)).eval() == z
    assert isinstance(ll(Integer.nameless(3)).eval(), lambda_term.App)
    assert isinstance(ll(Integer.nameless(-1)).eval(), lambda_term.App)
    assert isinstance(ll(String.nameless("w")).eval(), lambda_term.App)
