from . pgsn_ast import ASTNode, TmVar, TmAbs, TmApp, TmStr, TmFmtStr, TmGoal, TmStrat, TmEv, TmSet, TmMap,\
    TmRcd, TmRcdAcs, TmLet, TmFuncDef, TmIf, TmTrue, TmFalse, TmNot, TmAnd, TmOr, TmXor, TmEq, TmNull


def term_shift(d: int, t: ASTNode):
    def walk(c: int, t: ASTNode):
        match t:
            case TmVar(fi, x):
                if x >= c:
                    return TmVar(fi, x+d)
                else:
                    return TmVar(fi, x)
            case TmAbs(fi, x, t1):
                return TmAbs(fi, x, walk(c+1, t1))
            case TmApp(fi, t1, t2):
                return TmApp(fi, walk(c, t1), walk(c, t2))
            case TmStr(fi, t):
                return TmStr(fi, t)
            case TmFmtStr(fi, t_list):
                return TmFmtStr(fi, [walk(c, t) for t in t_list])
            case TmGoal(fi, t1, t2):
                return TmGoal(fi, walk(c, t1), walk(c, t2))
            case TmStrat(fi, t1, t2):
                return TmStrat(fi, walk(c, t1), walk(c, t2))
            case TmEv(fi, t):
                return TmEv(fi, walk(c, t))
            case TmSet(fi, t_list):
                return TmSet(fi, [walk(c, t) for t in t_list])
            case TmMap(fi, t1, t2):
                return TmMap(fi, walk(c, t1), walk(c, t2))
            case TmRcd(fi, a_list, t_list):
                return TmRcd(fi, a_list, [walk(c, t) for t in t_list])
            case TmRcdAcs(fi, t, a):
                return TmRcdAcs(fi, walk(c, t), a)

            case TmLet(fi, name, t1, t2):
                return TmLet(fi, name, walk(c, t1), walk(c, t2))
            case TmFuncDef(fi, name, t):
                return TmFuncDef(fi, name, walk(c, t))
            case TmIf(fi, t1, t2, t3):
                return TmIf(fi, walk(c, t1), walk(c, t2), walk(c, t3))
            case TmTrue(fi):
                return TmTrue(fi)
            case TmFalse(fi):
                return TmFalse(fi)
            case TmNot(fi, t):
                return TmNot(fi, walk(c, t))
            case TmAnd(fi, t1, t2):
                return TmAnd(fi, walk(c, t1), walk(c, t2))
            case TmOr(fi, t1, t2):
                return TmOr(fi, walk(c, t1), walk(c, t2))
            case TmXor(fi, t1, t2):
                return TmXor(fi, walk(c, t1), walk(c, t2))
            case TmEq(fi, t1, t2):
                return TmEq(fi, walk(c, t1), walk(c, t2))
            case TmNull(fi):
                return TmNull(fi)

    return walk(0, t)


def term_subst(j: int, s: ASTNode, t: ASTNode):
    def walk(c: int, t: ASTNode):
        match t:
            case TmVar(fi, x):
                if x == j + c:
                    return term_shift(c, s)
                else:
                    return TmVar(fi, x)
            case TmAbs(fi, x, t1):
                return TmAbs(fi, x, walk(c+1, t1))
            case TmApp(fi, t1, t2):
                return TmApp(fi, walk(c, t1), walk(c, t2))
            case TmStr(fi, t):
                return TmStr(fi, t)
            case TmFmtStr(fi, t_list):
                return TmFmtStr(fi, [walk(c, t) for t in t_list])
            case TmGoal(fi, t1, t2):
                return TmGoal(fi, walk(c, t1), walk(c, t2))
            case TmStrat(fi, t1, t2):
                return TmStrat(fi, walk(c, t1), walk(c, t2))
            case TmEv(fi, t):
                return TmEv(fi, walk(c, t))
            case TmSet(fi, t_list):
                return TmSet(fi, [walk(c, t) for t in t_list])
            case TmMap(fi, t1, t2):
                return TmMap(fi, walk(c, t1), walk(c, t2))
            case TmRcd(fi, a_list, t_list):
                return TmRcd(fi, a_list, [walk(c, t) for t in t_list])
            case TmRcdAcs(fi, t, a):
                return TmRcdAcs(fi, walk(c, t), a)

            case TmLet(fi, name, t1, t2):
                return TmLet(fi, name, walk(c, t1), walk(c, t2))
            case TmFuncDef(fi, name, t):
                return TmFuncDef(fi, name, walk(c, t))
            case TmIf(fi, t1, t2, t3):
                return TmIf(fi, walk(c, t1), walk(c, t2), walk(c, t3))
            case TmTrue(fi):
                return TmTrue(fi)
            case TmFalse(fi):
                return TmFalse(fi)
            case TmNot(fi, t):
                return TmNot(fi, walk(c, t))
            case TmAnd(fi, t1, t2):
                return TmAnd(fi, walk(c, t1), walk(c, t2))
            case TmOr(fi, t1, t2):
                return TmOr(fi, walk(c, t1), walk(c, t2))
            case TmXor(fi, t1, t2):
                return TmXor(fi, walk(c, t1), walk(c, t2))
            case TmEq(fi, t1, t2):
                return TmEq(fi, walk(c, t1), walk(c, t2))
            case TmNull(fi):
                return TmNull(fi)
    return walk(0, t)


def term_subst_top(s: ASTNode, t: ASTNode):
    return term_shift(-1, term_subst(0, term_shift(1, s), t))
