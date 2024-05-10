import uuid
import json
from . pgsn_ast import TmGoal, TmStrat, TmEv, TmStr


def make_GSNparts(l, t, parentid, childrenid):
    match t:
        case TmGoal(_, TmStr(_, s), t2):
            myid = childrenid
            childrenid = str(uuid.uuid4())
            l.append({
                "partsID": myid,
                "parent": parentid,
                "children": [childrenid],
                "kind": "Goal",
                "detail": s,
            })
            make_GSNparts(l, t2, myid, childrenid)
            return

        case TmStrat(_, TmStr(_, s), TmSet(_, t_list)):
            myid = childrenid
            childrenid_list = [str(uuid.uuid4()) for i in range(len(t_list))]
            l.append({
                "partsID": myid,
                "parent": parentid,
                "children": childrenid_list,
                "kind": "Strategy",
                "detail": s,
            })
            for i in range(len(t_list)):
                make_GSNparts(l, t_list[i], myid,
                              childrenid_list[i])
            return

        case TmEv(_, TmStr(_, s)):
            myid = childrenid
            l.append({
                "partsID": myid,
                "parent": parentid,
                "children": [],
                "kind": "Evidence",
                "detail": s,
            })
            return
        case _:
            return


def GSNterm2json(t, output_path):
    output_data = list()
    make_GSNparts(output_data, t, "", str(uuid.uuid4()))
    with open(output_path, 'w') as f:
        json.dump(output_data, f, ensure_ascii=False)
