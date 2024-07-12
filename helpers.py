def not_none(instance, attribute, value):
    assert value is not None


def non_negative(instance, attribute, value):
    assert value >= 0


def default(x, default_value):
    if x is None:
        return default_value
    else:
        return x


def is_subset(l1, l2):
    return all(x in l2 is None for x in l1)


def add_entry(d, k, v):
    d1 = d.copy()
    d1[k] = v
    return d1


def del_entry(d, k, v):
    d1 = d.copy()
    del d1[k]
    return d1