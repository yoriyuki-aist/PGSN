import stdlib


def test_data():
    s = stdlib.string('X')
    i = stdlib.integer(1)
    assert s.value == 'X'
    assert i.value == 1
