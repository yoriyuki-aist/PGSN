from . pgsn_ast import ASTNode, TmVar, TmAbs, TmApp, TmStr, TmFmtStr, TmGoal, TmStrat, TmEv, TmSet, TmMap, \
    TmRcd, TmRcdAcs, TmLet, TmFuncDef, TmIf, TmTrue, TmFalse, TmNot, TmAnd, TmOr, TmXor, TmEq
from . pgsn_assign import term_subst_top



class NoRuleApplies(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "[NoRuleApplies]"


def is_val(ctx: list, t: ASTNode):
    if is_GSNterm(t):
        return True
    else:
        match t:
            case TmAbs(_, _, _):
                return True
            case TmStr(_, _):
                return True
            case TmTrue(_):
                return True
            case TmFalse(_):
                return True
            case TmSet(_, t_list):
                for t_ in t_list:
                    if is_val(ctx, t_):
                        continue
                    else:
                        return False
                return True
            case TmRcd(_, _, t_list):
                for t_ in t_list:
                    if is_val(ctx, t_):
                        continue
                    else:
                        return False
                return True
            case _:
                return False


def is_TmStr(t):
    match t:
        case TmStr(_, _):
            return True
        case _:
            return False


def is_TmGoal(t):
    match t:
        case TmGoal(_, _, _):
            return True
        case _:
            return False


def is_TmStrat(t):
    match t:
        case TmStrat(_, _, _):
            return True
        case _:
            return False


def is_TmEv(t):
    match t:
        case TmEv(_, _):
            return True
        case _:
            return False


def is_TmSet(t):
    match t:
        case TmSet(_, _):
            return True
        case _:
            return False

def is_GSNterm(t):
    match t:
        case TmGoal(fi, t1, t2):
            if is_TmStr(t1):
                if is_TmEv(t2) or is_TmStrat(t2):
                    return is_GSNterm(t2)
                else:
                    return False
            else:
                return False

        case TmStrat(fi, t1, t2):
            if is_TmStr(t1):
                if is_TmSet(t2):
                    return is_GSNterm(t2)
                else:
                  return False
            else:
                return False

        case TmEv(fi, t1):
            if is_TmStr(t1):
                return True
            else:
                return False

        case TmSet(fi, t_list):
            for t_ in t_list:
                if is_TmGoal(t_):
                   if is_GSNterm(t_):
                      continue
                   else:
                      return False
                else:
                    return False
            return True
        case _:
            return False

def is_val_all(ctx: list, t_list: list):
    for t in t_list:
        if isinstance(t, TmVar):
            continue
        elif not is_val(ctx, t):
            return False
    else:
        return True


def is_str_all(ctx: list, t_list: list):
    for t in t_list:
        if isinstance(t, TmStr):
            continue
        else:
            return False
    else:
        return True


def list_eval1(ctx: list, t_list: list):
    evaled_list = []
    for t in t_list:
        if isinstance(t, TmVar):
            evaled_list.append(t)
        elif is_val(ctx, t):
            evaled_list.append(t)
        else:
            evaled_list.append(eval1(ctx, t))
    return evaled_list


def eval1(ctx: list, t: ASTNode):
    match t:
        case TmApp(fi, TmAbs(_, x, t12), v2) if is_val(ctx, v2):
            return term_subst_top(v2, t12)
        case TmApp(fi, v1, t2) if is_val(ctx, v1):
            t2_ = eval1(ctx, t2)
            return TmApp(fi, v1, t2_)
        case TmApp(fi, t1, t2):
            t1_ = eval1(ctx, t1)
            return TmApp(fi, t1_, t2)
        case TmFmtStr(fi, t_list) if not is_val_all(ctx, t_list):
            return TmFmtStr(fi, list_eval1(ctx, t_list))
        case TmFmtStr(fi, v_list) if is_str_all(ctx, v_list):
            s = ''
            for v in v_list:
                match v:
                    case TmStr(_, t):
                        s += t
            return TmStr(fi, s)
        case TmGoal(fi, v1, t2) if is_val(ctx, v1):
            return TmGoal(fi, v1, eval1(ctx, t2))
        case TmGoal(fi, t1, t2):
            return TmGoal(fi, eval1(ctx, t1), t2)
        case TmStrat(fi, v1, t2) if is_val(ctx, v1):
            return TmStrat(fi, v1, eval1(ctx, t2))
        case TmStrat(fi, t1, t2):
            return TmStrat(fi, eval1(ctx, t1), t2)
        case TmEv(fi, t):
            return TmEv(fi, eval1(ctx, t))

        case TmSet(fi, t_list) if not is_val_all(ctx, t_list):
            return TmSet(fi, list_eval1(ctx, t_list))
        case TmMap(_, TmAbs(fi_, x, t12), TmSet(fi, v2_list)):
            return TmSet(fi, [TmApp(fi_, TmAbs(fi_, x, t12), v2) for v2 in v2_list])

        case TmMap(fi, v1, t2) if is_val(ctx, v1):
            return TmMap(fi, v1, eval1(ctx, t2))
        case TmMap(fi, t1, t2):
            return TmMap(fi, eval1(ctx, t1), t2)

        case TmRcdAcs(_, TmRcd(_, a_list, t_list), a):
            for a_, t in zip(a_list, t_list):
                if a_ == a:
                    return t
        case TmRcd(fi, a_list, t_list) if not is_val_all(ctx, t_list):
            return TmRcd(fi, a_list, list_eval1(ctx, t_list))

        case TmLet(fi, name, v1, t2) if is_val(ctx, v1):
            return term_subst_top(v1, t2)
        case TmLet(fi, name, t1, t2):
            return TmLet(fi, name, eval1(ctx, t1), t2)
        case TmFuncDef(fi, name, t) if not is_val(ctx, t):
            return TmFuncDef(fi, name, eval1(ctx, t))

        case TmIf(_, TmTrue(_), t2, t3):
            return t2
        case TmIf(_, TmFalse(_), t2, t3):
            return t3
        case TmIf(fi, t1, t2, t3):
            return TmIf(eval1(ctx, t1), t2, t3)

        case TmNot(fi, TmTrue(_)):
            return TmFalse(fi)
        case TmNot(fi, TmFalse(_)):
            return TmTrue(fi)
        case TmNot(fi, t):
            return TmNot(fi, eval1(ctx, t))

        case TmAnd(fi, TmFalse(_), t2):
            return TmFalse(fi)
        case TmAnd(fi, TmTrue(_), t2):
            return t2
        case TmAnd(fi, t1, t2):
            return TmAnd(fi, eval1(ctx, t1), t2)

        case TmOr(fi, TmTrue(_), t2):
            return TmTrue(fi)
        case TmOr(fi, TmFalse(_), t2):
            return t2
        case TmOr(fi, t1, t2):
            return TmOr(fi, eval1(ctx, t1), t2)

        case TmXor(fi, TmTrue(_), t2):
            return TmNot(fi, t2)
        case TmXor(fi, TmFalse(_), t2):
            return t2
        case TmXor(fi, t1, t2):
            return TmXor(fi, eval1(ctx, t1), t2)

        case TmEq(fi, TmTrue(_), t2):
            return t2
        case TmEq(fi, TmFalse(_), t2):
            return TmNot(fi, t2)
        case TmEq(fi, TmStr(_, t1), TmStr(_, t2)):
            if t1 == t2:
                return TmTrue(fi)
            else:
                return TmFalse(fi)
        case TmEq(fi, t1, t2):
            return TmEq(fi, eval1(ctx, t1), t2)
        case _:
            raise NoRuleApplies


def pgsn_eval(ctx: list, t: ASTNode):
    try:
        return pgsn_eval(ctx, eval1(ctx, t))
    except NoRuleApplies:
        return t


def pick_boundvalue(ctx: list, index: int):     # TaPLにはない関数
    return ctx[index][1]


def ctx_eval(ctx: list):
    ctx_ = []
    for i, (s, b) in enumerate(ctx):
        b_ = pgsn_eval(ctx_, b)
        match b_:
            case TmVar(_, i):
                b_ = pick_boundvalue(ctx, i)
                print(b_)
        ctx_.append((s, b_))
    return ctx_
