def not_none(instance, attribute, value):
    assert value is not None


def non_negative(instance, attribute, value):
    assert value >= 0