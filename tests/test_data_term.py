import meta_info
import lambda_term
from data_term import Data, String, Integer
from data_term import Integer, String
import data_term


def test_data():
    s = data_term.string('X')
    i = data_term.integer(1)
    assert s.value == 'X'
    assert i.value == 1
