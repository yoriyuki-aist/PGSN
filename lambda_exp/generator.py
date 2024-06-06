from pyparsing import ParserElement
from . pgsn_ast import ASTNode, TmVar, TmAbs, TmApp, TmStr, TmFmtStr, TmGoal, TmStrat, TmEv, TmSet, TmMap,\
    TmRcd, TmRcdAcs, TmLet, TmFuncDef, TmIf, TmTrue, TmFalse, TmNot, TmAnd, TmOr, TmXor, TmEq
from . debug_info import DebugInfo

ParserElement.disable_memoization()
ParserElement.enable_left_recursion()


class TmpVar(ASTNode):
    _fields = ('name',)
    __match_args__ = ('fi', 'name',)

    def __init__(self, fi: DebugInfo, name: str):
        super().__init__(fi)
        self.name = name

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class AstGenerator:
    def __init__(self):
        self.ctx = []

    def make_TmAbs(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.x = tokens[0]
        self.t1 = tokens[1]
        return TmAbs(self.fi, self.x, self.t1)

    def make_TmApp(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t1 = tokens[0]
        self.t2 = tokens[1]
        return TmApp(self.fi, self.t1, self.t2)

    def make_TmpVar(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.name = tokens[0]
        return TmpVar(self.fi, self.name)

    def make_TmStr(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t = tokens[0]
        return TmStr(self.fi, self.t)

    def make_TmFmtStr(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t_list = tokens.as_list()
        return TmFmtStr(self.fi, self.t_list)

    def make_TmGoal(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t1 = tokens[0]
        self.t2 = tokens[1]
        return TmGoal(self.fi, self.t1, self.t2)

    def make_TmStrat(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t1 = tokens[0]
        self.t2 = tokens[1]
        return TmStrat(self.fi, self.t1, self.t2)

    def make_TmEv(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t = tokens[0]
        return TmEv(self.fi, self.t)

    def make_TmSet(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t_list = tokens
        return TmSet(self.fi, self.t_list)

    def make_TmMap(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t1 = tokens[0]
        self.t2 = tokens[1]
        return TmMap(self.fi, self.t1, self.t2)

    def make_TmRcd(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.a_list = []
        self.t_list = []
        for self.a, self.t in tokens.as_list():
            self.a_list.append(self.a)
            self.t_list.append(self.t)
        return TmRcd(self.fi, self.a_list, self.t_list)

    def make_TmRcdAcs(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t = tokens[0]
        self.a = tokens[1]
        return TmRcdAcs(self.fi, self.t, self.a)

    def make_TmLet(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.name = tokens[0]
        self.t1 = tokens[1]
        self.t2 = tokens[2]
        return TmLet(self.fi, self.name, self.t1, self.t2)

    def LetIdent(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.name = tokens[0]
        self.t1 = tokens[1]
        self.t2 = tokens[2]
        return TmApp(self.fi, TmAbs(self.fi, self.name, self.t2), self.t1)

    def make_TmFuncDef(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.name = tokens[0]
        self.args = tokens[1]
        self.t = tokens[2]
        for self.arg in reversed(self.args):
            self.t = TmAbs(self.fi, self.arg, self.t)
        return TmFuncDef(self.fi, self.name, self.t)

    def make_FuncCall(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t = TmpVar(self.fi, tokens[0])
        self.args = tokens[1]
        for self.arg in self.args:
            self.t = TmApp(self.fi, self.t, self.arg)
        return self.t

    def make_TmTrue(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        return TmTrue(self.fi)

    def make_TmFalse(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        return TmFalse(self.fi)

    def make_TmNot(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t = tokens[0][0]
        return TmNot(self.fi, self.t)

    def make_TmAnd(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t1 = tokens[0][0]
        self.t2 = tokens[0][1]
        return TmAnd(self.fi, self.t1, self.t2)

    def make_TmOr(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t1 = tokens[0][0]
        self.t2 = tokens[0][1]
        return TmOr(self.fi, self.t1, self.t2)

    def make_TmXor(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t1 = tokens[0][0]
        self.t2 = tokens[0][1]
        return TmXor(self.fi, self.t1, self.t2)

    def make_TmEq(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t1 = tokens[0][0]
        self.t2 = tokens[0][1]
        return TmEq(self.fi, self.t1, self.t2)

    def make_TmIf(self, source, location, tokens):
        self.fi = DebugInfo(source, location)
        self.t1 = tokens[0]
        self.t2 = tokens[1]
        self.t3 = tokens[2]
        return TmIf(self.fi, self.t1, self.t2, self.t3)

    def calc_index(self, name: str, ctx: list):
        index = 0
        for i, (s, b) in enumerate(ctx):
            if s == name:
                return index
            index += 1
        else:
            return -1

    def set_index(self, tm: ASTNode, ctx: list, c: int):
        match tm:
            case TmpVar(fi, name):
                return TmVar(fi, self.calc_index(name, ctx))
            case TmAbs(fi, x, t1):
                return TmAbs(fi, x, self.set_index(t1, [(x, t1)]+ctx, c+1))
            case TmApp(fi, t1, t2):
                return TmApp(fi, self.set_index(t1, ctx, c), self.set_index(t2, ctx, c))
            case TmStr(fi, t):
                return TmStr(fi, t)
            case TmFmtStr(fi, t_list):
                return TmFmtStr(fi, [self.set_index(t, ctx, c) for t in t_list])
            case TmGoal(fi, t1, t2):
                return TmGoal(fi, self.set_index(t1, ctx, c), self.set_index(t2, ctx, c))
            case TmStrat(fi, t1, t2):
                return TmStrat(fi, self.set_index(t1, ctx, c), self.set_index(t2, ctx, c))
            case TmEv(fi, t):
                return TmEv(fi, self.set_index(t, ctx, c))
            case TmSet(fi, t_list):
                return TmSet(fi, [self.set_index(t, ctx, c) for t in t_list])
            case TmMap(fi, t1, t2):
                return TmMap(fi, self.set_index(t1, ctx, c), self.set_index(t2, ctx, c))
            case TmRcd(fi, a_list, t_list):
                return TmRcd(fi, a_list, [self.set_index(t, ctx, c) for t in t_list])
            case TmRcdAcs(fi, t, a):
                return TmRcdAcs(fi, self.set_index(t, ctx, c), a)
            case TmVar(fi, x):
                return TmVar(fi, x)
            case TmLet(fi, name, t1, t2):
                return TmLet(fi, name, self.set_index(t1, ctx, c), self.set_index(t2, [(name, t1)]+ctx, c+1))
            case TmFuncDef(fi, name, t):
                return TmFuncDef(fi, name, self.set_index(t, ctx, c))
            case TmTrue(fi):
                return TmTrue(fi)
            case TmFalse(fi):
                return TmFalse(fi)
            case TmNot(fi, t):
                return TmNot(fi, self.set_index(t, ctx, c))
            case TmAnd(fi, t1, t2):
                return TmAnd(fi, self.set_index(t1, ctx, c), self.set_index(t2, ctx, c))
            case TmOr(fi, t1, t2):
                return TmOr(fi, self.set_index(t1, ctx, c), self.set_index(t2, ctx, c))
            case TmXor(fi, t1, t2):
                return TmXor(fi, self.set_index(t1, ctx, c), self.set_index(t2, ctx, c))
            case TmEq(fi, t1, t2):
                return TmEq(fi, self.set_index(t1, ctx, c), self.set_index(t2, ctx, c))
            case TmIf(fi, t1, t2, t3):
                return TmIf(fi, self.set_index(t1, ctx, c), self.set_index(t2, ctx, c), self.set_index(t3, ctx, c))
