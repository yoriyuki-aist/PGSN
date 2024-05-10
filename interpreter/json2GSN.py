import json
import sys
from . debug_info import DebugInfo
from . pgsn_ast import TmGoal, TmStrat, TmEv, TmStr, TmSet



input_path = sys.argv[1]

json_open = open(input_path, 'r')
PGSN_parts = json.load(json_open)


GSN_tree = {}
top_goal_id = ''
for part in PGSN_parts:
    if part['parent'] == '':
        top_goal_id = part['partsID']
    GSN_tree[part['partsID']] = {'children':part['children'], 'kind':part['kind'], 'detail':part['detail']}

def make_GSNtree(GSN_tree, partid):
     match GSN_tree[partid]['kind']:
        case 'Goal':
            return TmGoal(DebugInfo(), TmStr(DebugInfo(), GSN_tree[partid]['detail']), make_GSNtree(GSN_tree, GSN_tree[partid]['children'][0]))
        case 'Strategy':
            return TmStrat(DebugInfo(), TmStr(DebugInfo(), GSN_tree[partid]['detail']), TmSet(DebugInfo(), [make_GSNtree(GSN_tree, i) for i in GSN_tree[partid]['children']]))
        case 'Evidence':
            return TmEv(DebugInfo(), TmStr(DebugInfo(), GSN_tree[partid]['detail']))            
         
t = make_GSNtree(GSN_tree, top_goal_id)

print(t) 
