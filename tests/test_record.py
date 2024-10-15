import meta_info
import lambda_term
from record_term import Record
from data_term import Integer, String
import data_term


def test_record():
    x = lambda_term.constant('x')
    y = lambda_term.constant('y')
    z = lambda_term.constant('z')
    r = Record.named(attributes={'x': x, 'y': y, 'z': z})
    k1 = data_term.string('x')
    k2 = data_term.string('w')
    assert r(k1).eval() == x.eval()
    assert r(k2).eval_or_none() is None
