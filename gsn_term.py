from object_term import *
from stdlib import lambda_abs_keywords

gsn_class = define_class('GSN', base_class,
                         gsn_type='Node')

support_class = define_class('Support', gsn_class, {})
undeveloped = instantiate(support_class, description='Undeveloped', gsn_type='Undeveloped')
evidence_class = define_class('Evidence', support_class, gsn_type='Evidence')
strategy_class = define_class('Strategy', support_class, gsn_type='Strategy')

goal_class = define_class('Goal', gsn_class,
                          gsn_type='Goal',
                          assumptions=[],
                          contexts=[],
                          support=undeveloped
                          )
assumption_class = define_class('Assumption', gsn_class, gsn_type='Assumption')
context_class = define_class('Context', gsn_class, gsn_type='Context')

_d = variable('x')
_support = variable('support')
_assumptions = variable('assumptions')
_contexts = variable('contexts')
_sub_goals = variable('sub_goals')

evidence = lambda_abs_keywords(arguments={'description': _d},
                               body=instantiate(evidence_class)({'description': _d}))
strategy = lambda_abs_keywords(arguments={'description': _d, 'sub_goals': _sub_goals},
                               body=instantiate(strategy_class)({'description': _d, 'sub_goals': _sub_goals}))
goal = lambda_abs_keywords(arguments={'description': _d,
                                      'assumptions': _assumptions,
                                      'contexts': _contexts,
                                      'support': _support},
                           defaults=stdlib.record({
                               'assumptions': stdlib.empty,
                               'contexts': stdlib.empty}),
                           body=instantiate(goal_class)({'description': _d, 'support': _support}))
assumption = lambda_abs_keywords(arguments={'description': _d},
                                 body=instantiate(assumption_class)({'description': _d}))
context = lambda_abs_keywords(arguments={'description': _d},
                              body=instantiate(context_class)({'description': _d}))
