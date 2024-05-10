from pyparsing import MatchFirst, Suppress, Keyword, Forward, Word, unicode, ZeroOrMore, identchars, identbodychars, \
    DelimitedList, Group, alphanums, infix_notation, OpAssoc, Opt
from . pgsn_astgenerator import AstGenerator


def pgsn_parser(FV_ctx, input_data):
    ast = AstGenerator()
    ast.ctx = ast.ctx + FV_ctx

    # STRATEGYの項をstr(t1, t2)からstrat(t1, t2)に変更する場合は次の行のstrをstratに変更する 
    (LAMBDA, GOAL, STRATEGY, EVIDENCE, MAP, LET, IN, TRUE, FALSE, IF, THEN, ELSE, NOT, AND, OR, XOR) = map(Suppress, list(map(Keyword,
                                                                                                                              "lambda, goal, str, ev, map, let, in, TRUE, FALSE, if, then, else, not, and, or, xor".replace(",", "").split())))
    keywords = MatchFirst((LAMBDA, GOAL, STRATEGY, EVIDENCE,
                          MAP, LET, IN, TRUE, FALSE, IF, THEN, ELSE, NOT, AND, OR, XOR))

    LPAREN, RPAREN, LBRACE, RBRACE, LBRACK, RBRACK, COMMA, COLON, DOT, DOUBLE_QUOTATION, EQUAL = map(
        Suppress, '(){}[],:."=')

    term = Forward()

    identifier = ~keywords + Word(identchars, identbodychars)
    identifier.set_name('identifier')

    constString = Word(unicode.printables, exclude_chars='{}"') # unicode.printablesは日本語などを扱うのに必要
    string = (DOUBLE_QUOTATION + Word(unicode.printables,   # unicode.printablesは日本語などを扱うのに必要
              exclude_chars='{}"') + DOUBLE_QUOTATION)
    string.set_name('string')
    constString.set_parse_action(ast.make_TmStr)
    string.set_parse_action(ast.make_TmStr)

    const = (TRUE | FALSE | string)

    TRUE.set_parse_action(ast.make_TmTrue)
    FALSE.set_parse_action(ast.make_TmFalse)

    fmtString = (DOUBLE_QUOTATION + ZeroOrMore(((LBRACE + term +
                 RBRACE) | constString)) + DOUBLE_QUOTATION)

    fmtString.set_name('fmtString')
    fmtString.set_parse_action(ast.make_TmFmtStr)

    lambdaAbs = LAMBDA + identifier + DOT + term
    lambdaAbs.set_name('lambdaAbs')
    lambdaAbs.set_parse_action(ast.make_TmAbs)

    lambdaApp = LPAREN + term + term + RPAREN
    lambdaApp.set_name('lambdaApp')
    lambdaApp.set_parse_action(ast.make_TmApp)

    var = (~keywords + Word(identchars, identbodychars))
    var.set_name('var')
    var.set_parse_action(ast.make_TmpVar)

    goal = GOAL + LPAREN + term + COMMA + term + RPAREN
    goal.set_name('goal')
    goal.set_parse_action(ast.make_TmGoal)

    strategy = STRATEGY + LPAREN + term + COMMA + term + RPAREN
    strategy.set_name('strategy')
    strategy.set_parse_action(ast.make_TmStrat)

    evidence = EVIDENCE + LPAREN + term + RPAREN
    evidence.set_name('evidence')
    evidence.set_parse_action(ast.make_TmEv)

    sets = (LBRACE + DelimitedList(term) + RBRACE) | (LBRACE + RBRACE)
    sets.set_name('sets')
    sets.set_parse_action(ast.make_TmSet)

    maps = MAP + LPAREN + term + COMMA + term + RPAREN
    maps.set_name('maps')
    maps.set_parse_action(ast.make_TmMap)

    records = (
        LBRACE + DelimitedList(Group(Word(alphanums + "_") + COLON + term)) + RBRACE)
    records.set_name('records')
    records.set_parse_action(ast.make_TmRcd)

    rcdAccess = (term + DOT + Word(alphanums + "_"))
    rcdAccess.set_name('rcdAccess')
    rcdAccess.set_parse_action(ast.make_TmRcdAcs)

    identDecl = (LET + identifier + EQUAL)
    identDef = (identDecl + term + IN + term)
    identDef.set_name('identDef')

    identDef.set_parse_action(ast.LetIdent)  # TmApp(TmAbs())を使う場合
    # identDef.set_parse_action(ast.make_TmLet) # TmLetを使う場合

    funcDecl = (identifier + Group(LPAREN +
                Opt(DelimitedList(identifier)) + RPAREN) + EQUAL)
    funcDef = (funcDecl + term)
    funcDef.set_name('funcDef')
    funcDef.set_parse_action(ast.make_TmFuncDef)

    funcCall = (identifier + Group(LPAREN + Opt(DelimitedList(term)) + RPAREN))
    funcCall.set_name('funcCall')
    funcCall.set_parse_action(ast.make_FuncCall)

    ifElse = (IF + term + THEN + term + ELSE + term)
    ifElse.set_name('if')
    ifElse.set_parse_action(ast.make_TmIf)

    eq_ = Group(string + (EQUAL + EQUAL) + string)
    eq_.set_name('eq')
    eq_.set_parse_action(ast.make_TmEq)

    bool_term = infix_notation((TRUE | FALSE | eq_),
                               [
        (NOT, 1, OpAssoc.RIGHT, ast.make_TmNot),
        (AND, 2, OpAssoc.LEFT, ast.make_TmAnd),
        (OR, 2, OpAssoc.LEFT, ast.make_TmOr),
        (XOR, 2, OpAssoc.LEFT, ast.make_TmXor),
        ((EQUAL + EQUAL), 2, OpAssoc.LEFT, ast.make_TmEq),
    ])

    term_ = (LPAREN + term + RPAREN)
    term_.set_name('term')
    term <<= (lambdaAbs | lambdaApp | goal | strategy | evidence | maps | rcdAccess | records |
              sets | identDef | funcDef | ifElse | funcCall | bool_term | string | fmtString | var | term_)
    term.set_name('term')

    parseTree = term.parse_string(input_data, parseAll=True)
    t = ast.set_index(parseTree[0], FV_ctx, 0)
    for i, (s, b) in enumerate(ast.ctx):
        t_ = ast.set_index(b, ast.ctx, 0)
        ast.ctx[i] = (s, t_)
    return t, ast.ctx
