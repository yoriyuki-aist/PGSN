from . pgsn_ast import TmStr, TmGoal, TmStrat, TmEv, TmSet

# GSNの形式をしていないときに発生させる例外
class NoGSNTerm(Exception):
    def __init__(self, fi):
        self.fi = fi

    def __str__(self):
        return f'{self.fi}'

# 文字列かどうかの判定
def is_TmStr(t):
    match t:
        case TmStr(_, _):
            return True
        case _:
            return False

# Goalノードかどうかの判定
def is_TmGoal(t):
    match t:
        case TmGoal(_, _, _):
            return True
        case _:
            return False

# Strategyノードかどうかの判定
def is_TmStrat(t):
    match t:
        case TmStrat(_, _, _):
            return True
        case _:
            return False

# Evidenceノードかどうかの判定
def is_TmEv(t):
    match t:
        case TmEv(_, _):
            return True
        case _:
            return False

# 集合かどうかの判定
def is_TmSet(t):
    match t:
        case TmSet(_, _):
            return True
        case _:
            return False

# GSNの形式をしているかどうかの判定
def check_GSNform(t):
    match t:
        case TmGoal(fi, t1, t2):   # goal(t1, t2)ならばt1はstringでt2はevidenceかstrategy
            if is_TmStr(t1):
                if is_TmEv(t2) or is_TmStrat(t2):
                    return check_GSNform(t2)
            else:
                raise NoGSNTerm(fi)
                # return False

        case TmStrat(fi, t1, t2):   # strat(t1, t2)ならばt1はstringでt2はset
            if is_TmStr(t1):
                if is_TmSet(t2):
                    return check_GSNform(t2)
            else:
                raise NoGSNTerm(fi)
                # return False

        case TmEv(fi, t1):  # ev(t1)ならばt1はstring
            if is_TmStr(t1):
                return True
            else:
                raise NoGSNTerm(fi)
                # return False

        case TmSet(fi, t_list): # {t1, ..., tn}ならばtkは全てgoal
            for t_ in t_list:
                if is_TmGoal(t_):
                    check_GSNform(t_)
                else:
                    raise NoGSNTerm(fi)
                    # return False
            return True

        case _: # Undevelopedなどを追加する場合はこの上に追加する
            print("No GSN term")
            return False
