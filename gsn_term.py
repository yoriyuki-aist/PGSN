from object_term import *

gsn_class = define_class('GSN', base_class,
                         gsn_type='Node',
                         description=None)

support_class = define_class('Support', gsn_class)
undeveloped = instantiate(support_class, description='Undeveloped', gsn_type='Undeveloped')
evidence_class = define_class('Evidence', support_class, gsn_type='Evidence')
strategy_class = define_class('Strategy', support_class, gsn_type='Strategy', subgoals=[])

goal_class = define_class('Goal', gsn_class,
                          gsn_type='Goal',
                          assumptions=[],
                          contexts=[],
                          support=undeveloped
                          )
assumption_class = define_class('Assumption', gsn_class, gsn_type='Assumption')
context_class = define_class('Context', gsn_class, gsn_type='Context')