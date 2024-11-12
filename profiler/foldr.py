import os
import sys
#sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import list_term
import stdlib
import cProfile

def test_fold():
    i1 = stdlib.integer(1)
    i2 = stdlib.integer(1)
    ll = stdlib.cons(i1)(stdlib.cons(i2)(list_term.empty))
    i = stdlib.integer_sum(ll)
    assert i.fully_eval().value == 2


if __name__ == '__main__':
    cProfile.run('test_fold()')