from . pgsn_ast import ASTNode, TmVar, TmAbs, TmApp, TmStr, TmFmtStr, TmGoal, TmStrat, TmEv, TmSet, TmMap,\
    TmRcd, TmRcdAcs, TmLet, TmFuncDef, TmIf, TmTrue, TmFalse, TmNot, TmAnd, TmOr, TmXor, TmEq, TmNull


def ctxlength(ctx: list): # コンテキストの長さを返す
    return len(ctx)


def pick_freshname(ctx: list, x: str):  # 名前の重複がある際に付け替える
    for (s, b) in ctx:
        if s == x:
            return pick_freshname(ctx, x + "'")
    else:
        return ([(x, TmStr(DebugInfo('', 0), 'namebind_'+str(len(ctx))))] + ctx, x)


def index2name(ctx: list, x: int):  # インデックスを名前に変換
    for i, (s, b) in enumerate(ctx):
        if i == x:
            return s
    print('[Not Bound]', end='')
    return ''


def print_tm(ctx: list, t: ASTNode):  # 項の出力
    match t:
        case TmAbs(fi, x, t1):
            (ctx_, x_) = pick_freshname(ctx, x)
            # print(f'(λ {x_}. ', end='')
            print(f'(lambda {x_}. ', end='')
            print_tm(ctx_, t1)
            print(')', end='')

        case TmApp(fi, t1, t2):
            print('(', end='')
            print_tm(ctx, t1)
            print(' ', end='')
            print_tm(ctx, t2)
            print(')', end='')
        case TmVar(fi, x):
            # t_ = pick_boundvalue(ctx, x)
            # print_tm(ctx, t_)
            print(f'{index2name(ctx, x)}', end='')

        case TmStr(fi, t):
            print(f'\"{t}\"', end='')

        case TmFmtStr(fi, t_list):
            print(f'\"', end='')
            for t_ in t_list:
                match t_:
                    case TmStr(v):
                        print(f'{v}', end='')
                    case _:
                        print('{', end='')
                        print_tm(ctx, t_)
                        print('}', end='')
            print(f'\"', end='')

        case TmGoal(fi, t1, t2):
            print('goal(', end='')
            print_tm(ctx, t1)
            print(', ', end='')
            print_tm(ctx, t2)
            print(')', end='')

        case TmStrat(fi, t1, t2): 
            print('str(', end='') # 項の出力においてstrategyをstratと表示させたい場合はここを変更する
            print_tm(ctx, t1)
            print(', ', end='')
            print_tm(ctx, t2)
            print(')', end='')

        case TmEv(fi, t):
            print('ev(', end='')
            print_tm(ctx, t)
            print(')', end='')

        case TmSet(fi, t_list):
            print('{', end='')
            for t in t_list:
                print_tm(ctx, t)
                print(', ', end='')
            print('}', end='')

        case TmMap(fi, t1, t2):
            print('map(', end='')
            print_tm(ctx, t1)
            print(', ', end='')
            print_tm(ctx, t2)
            print(')', end='')

        case TmRcd(fi, a_list, t_list):
            print('{', end='')
            for a, t in zip(a_list, t_list):
                print(f'{a}:', end='')
                print_tm(ctx, t)
                print(', ', end='')
            print('}', end='')

        case TmRcdAcs(fi, t, a):
            print_tm(ctx, t)
            print(f'.{a}', end='')

        case TmLet(fi, name, t1, t2):
            (ctx_, name_) = pick_freshname(ctx, name)
            print(f'let {name_} = ', end='')
            print_tm(ctx_, t1)
            print(f' in ', end='')
            print_tm(ctx_, t2)

        case TmFuncDef(fi, name, t):
            print(f'{name} = ', end='')
            print_tm(ctx, t)

        case TmIf(fi, t1, t2, t3):
            print('if ', end='')
            print_tm(ctx, t1)
            print(' then ', end='')
            print_tm(ctx, t2)
            print(' else ', end='')
            print_tm(ctx, t3)

        case TmTrue(fi):
            print('TRUE', end='')

        case TmFalse(fi):
            print('FALSE', end='')

        case TmNot(fi, t):
            print('not ', end='')
            print_tm(ctx, t)

        case TmAnd(fi, t1, t2):
            print_tm(ctx, t1)
            print(' and ', end='')
            print_tm(ctx, t2)

        case TmOr(fi, t1, t2):
            print_tm(ctx, t1)
            print(' or ', end='')
            print_tm(ctx, t2)

        case TmXor(fi, t1, t2):
            print_tm(ctx, t1)
            print(' xor ', end='')
            print_tm(ctx, t2)

        case TmEq(fi, t1, t2):
            print_tm(ctx, t1)
            print(' == ', end='')
            print_tm(ctx, t2)

        case TmNull(fi):
            print('NULL', end='')
