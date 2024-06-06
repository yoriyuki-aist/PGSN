from lambda_term import *
def test_goal():
    assert goal.eval({}) is None
    assert goal.shift() == goal
    assert goal.subst(strategy) == goal


