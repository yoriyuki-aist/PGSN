def not_none(instance, attribute, value):
    assert value is not None


def non_negative(instance, attribute, value):
    assert value >= 0


def default(x, default_value):
    if x is None:
        return default_value
    else:
        return x