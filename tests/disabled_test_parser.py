from interpreter.pgsn_parser import pgsn_parser
from interpreter.pgsn_ast import *


# pgsn_parser(FV_ctx, input_data)
# return t, ast.ctx

def test_parser_01():
    source = '"str1"'
    assert pgsn_parser([], source) == (
        TmStr(DebugInfo(source, 0), 'str1'), [])


def test_parser_02():
    source = 'ev("t")'
    assert pgsn_parser([], source) == (
        TmEv(DebugInfo(source, 0), TmStr(DebugInfo(source, 3), 't')), [])


def test_parser_03():
    source = 'goal("t1","t2")'
    assert pgsn_parser([], source) == (
        TmGoal(DebugInfo(source, 0), TmStr(DebugInfo(source, 5), 't1'), TmStr(DebugInfo(source, 10), 't2')), [])


def test_parser_04():
    source = 'strat("t1","t2")'
    assert pgsn_parser([], source) == (
        TmStrat(DebugInfo(source, 0), TmStr(DebugInfo(source, 6), 't1'), TmStr(DebugInfo(source, 11), 't2')), [])


def test_parser_05():
    source = 'goal("g1", ev("e1"))'
    assert pgsn_parser([], source) == (
        TmGoal(DebugInfo(source, 0), TmStr(DebugInfo(source, 5), 'g1'), TmEv(DebugInfo(source, 11), TmStr(DebugInfo(source, 14), 'e1'))), [])


def test_parser_06():
    source = '{}'
    assert pgsn_parser([], source) == (
        TmSet(DebugInfo(source, 0), []), [])


def test_parser_07():
    source = '{goal("g2", ev("e1"))}'
    assert pgsn_parser([], source) == (
        TmSet(DebugInfo(source, 0), [TmGoal(DebugInfo(source, 1), TmStr(DebugInfo(source, 6), 'g2'), TmEv(DebugInfo(source, 12), TmStr(DebugInfo(source, 15), 'e1')))]), [])


def test_parser_08():
    source = 'goal("g1", strat("s1",{}))'
    assert pgsn_parser([], source) == (
        TmGoal(DebugInfo(source, 0), TmStr(DebugInfo(source, 5), 'g1'), TmStrat(DebugInfo(source, 11), TmStr(DebugInfo(source, 17), 's1'), TmSet(DebugInfo(source, 22), []))), [])


def test_parser_09():
    source = 'goal("g1",strat("s1",{goal("g2",ev("e1"))}))'
    assert pgsn_parser([], source) == (
        TmGoal(DebugInfo(source, 0), TmStr(DebugInfo(source, 5), 'g1'), TmStrat(DebugInfo(source, 10), TmStr(DebugInfo(source, 16), 's1'), TmSet(DebugInfo(source, 21), [TmGoal(DebugInfo(source, 22), TmStr(DebugInfo(source, 27), 'g2'), TmEv(DebugInfo(source, 32), TmStr(DebugInfo(source, 35), 'e1')))]))), [])


def test_parser_10():
    source = 'x'
    assert pgsn_parser([], source) == (
        TmVar(DebugInfo(source, 0), -1), [])


def test_parser_11():
    source = 'map("t1", "t2")'
    assert pgsn_parser([], source) == (
        TmMap(DebugInfo(source, 0), TmStr(DebugInfo(source, 4), 't1'), TmStr(DebugInfo(source, 10), 't2')), [])


def test_parser_12():
    source = 'lambda x.x'
    assert pgsn_parser([], source) == (
        TmAbs(DebugInfo(source, 0), 'x', TmVar(DebugInfo(source, 9), 0)), [])


def test_parser_13():
    source = '("t1" "t2")'
    assert pgsn_parser([], source) == (
        TmApp(DebugInfo(source, 0), TmStr(DebugInfo(source, 1), 't1'), TmStr(DebugInfo(source, 6), 't2')), [])


def test_parser_14():
    source = '{a:"t"}'
    assert pgsn_parser([], source) == (
        TmRcd(DebugInfo(source, 0), ['a'], [TmStr(DebugInfo(source, 3), 't')]), [])
