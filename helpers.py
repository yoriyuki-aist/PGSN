from inspect import signature


def not_none(instance, attribute, value):
    assert value is not None


def non_negative(instance, attribute, value):
    assert value >= 0


def fun_with_arity_n (f, n):
    if not callable(f):
        return False
    sig = signature(f)
    if len(sig.parameters) == n:
        return True
    else:
        return False


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


def check_type_list(x, types):
    if not type(x) is list:
        return False
    if not len(x) == len(types):
        return False
    for y, c in zip(x, types):
        if not isinstance(y, c):
            return False
    return True


def check_type_dict(x, types):
    if not type(x) is dict:
        return False
    if not set(x.keys()) == set(types.keys()):
        return False
    for k in types.keys():
        if not isinstance(x[k], types[k]):
            return False
    return True



