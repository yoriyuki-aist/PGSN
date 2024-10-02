import meta_info
import lambda_term
from data_term import Data, String, Integer
from data_term import Integer, String


def test_data():
    s = String.named(value='X')
    i = Integer.named(value=1)
    assert s.value == 'X'
    assert i.value == 1
