import sys

sys.path.append("..")
import json
from gsn_term import *
import gsn

robot = goal(description="There is no known vulnerability in the robot",
             support=strategy(description="Argument over each vulnerability",
                              subgoals=[
                                  goal(description="Vulnerability A is not exploited",
                                       support=evidence(description="Test results")),
                                  goal(description="Vulnerability B is not exploited",
                                       support=evidence(description="Test results"))
                              ]
                              )
             )

web_server = goal(description="The server can deal with DoS attacks on the server",
                  support=evidence(description="Access restriction"))

system = goal(description="The robot does not make unintended movements",
              support=strategy(description="Argument over the robot and the server",
                               subgoals=[
                                   goal(description="The robot behaves according to commands",
                                        support=strategy(description="Argument over each threat",
                                                         subgoals=[robot]
                                                         )),
                                   goal(description="The server gives correct commands to the robot",
                                        support=strategy(description="Argument over each threat",
                                                         subgoals=[web_server])
                                        )
                               ]
                               )
              )

s = strategy(description="Argument over each vulnerability",
                              subgoals=[
                                  goal(description="Vulnerability A is not exploited",
                                       support=evidence(description="Test results")),
                                  goal(description="Vulnerability B is not exploited",
                                       support=evidence(description="Test results"))
                              ]
                              )

if __name__ == '__main__':
    # n = gsn.pgsn_to_gsn(evidence_class, steps=10000)
    # print(json.dumps(gsn.python_val(n), sort_keys=True, indent=4))
    #print(s('subgoals').fully_eval())
    print(system.fully_eval(steps=10000))
    n = gsn.pgsn_to_gsn(system, steps=10000)
    print(json.dumps(gsn.python_val(n), sort_keys=True, indent=4))
