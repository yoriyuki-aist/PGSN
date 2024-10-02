import meta_info
import lambda_term
from record_term import Record
from data_term import Integer, String


def test_record():
    x = lambda_term.constant('x')
    y = lambda_term.constant('y')
    z = lambda_term.constant('z')
    r = Record.named(terms=(('x', x), ('y', y), ('z', z)))
    assert r.terms == (('x', x), ('y', y), ('z', z))
