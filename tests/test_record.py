import meta_info
import lambda_term
from record_term import Record
from data_term import Integer, String


def test_record():
    x = lambda_term.Constant.nameless('x')
    y = lambda_term.Constant.nameless('y')
    z = lambda_term.Constant.nameless('z')
    r = Record.nameless((('x', x), ('y', y), ('z', z)))
    assert r(String.nameless('x')).eval() == x
    assert r(String.nameless('y')).eval() == y
    assert r(String.nameless('z')).eval() == z
    assert isinstance(r(Integer.nameless(3)).eval(), lambda_term.App)
    assert isinstance(r(String.nameless('a')).eval(), lambda_term.App)
