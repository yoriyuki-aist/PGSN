import meta_info
import lambda_term
from list_term import Record
from data_term import Integer, String


def test_list():
    x = lambda_term.Constant.named('x')
    y = lambda_term.Constant.named('y')
    z = lambda_term.Constant.named('z')
    r = Record.named((('x', x), ('y', y), ('z', z)))
    r1 = r.remove_name()
    assert r1(String.nameless('x')).eval() == x
    assert r1(String.nameless('y')).eval() == y
    assert r1(Integer.nameless('z')).eval() == z
    assert isinstance(r1(Integer.nameless(3)).eval(), lambda_term.App)
    assert isinstance(r1(String.nameless('a')).eval(), lambda_term.App)
