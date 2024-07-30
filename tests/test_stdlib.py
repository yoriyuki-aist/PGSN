import meta_info
import lambda_term
import string_term
import list_term
import record_term
import stdlib


def test_empty_list():
    assert stdlib.empty_list.terms == []

