from __future__ import annotations
import abc
from enum import Enum
from attrs import define, field, frozen
from meta_info.meta_info import MetaInfo
from helpers import helpers


class Updated(Enum):
    YES = 1
    NO = 0


@frozen(kw_only=True)
class Term:
    meta_info: MetaInfo = MetaInfo.empty()

    @abc.abstractmethod
    def eval(self) -> Term:
        pass


@frozen
class Var(Term):
    __match_args__ = ('x',)
    x: int = field(validator=helpers.non_negative)

    def eval(self):
        return Updated.NO, self


@frozen
class Abs(Term):
    t: Term = field(validator=helpers.not_none)



class TmAbs(ASTNode):
    _fields = ('x', 't1')
    __match_args__ = ('fi', 'x', 't1')

    def __init__(self, fi: DebugInfo, x: str, t1: ASTNode):
        super().__init__(fi)
        self.x = x
        self.t1 = t1

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmApp(ASTNode):
    _fields = ('t1', 't2')
    __match_args__ = ('fi', 't1', 't2')

    def __init__(self, fi: DebugInfo, t1: ASTNode, t2: ASTNode):
        super().__init__(fi)
        self.t1 = t1
        self.t2 = t2

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmStr(ASTNode):
    _fields = ('t',)
    __match_args__ = ('fi', 't',)

    def __init__(self, fi: DebugInfo, t: ASTNode):
        super().__init__(fi)
        self.t = t

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmFmtStr(ASTNode):
    _fields = ('t_list',)
    __match_args__ = ('fi', 't_list',)

    def __init__(self, fi: DebugInfo, t_list: list):
        super().__init__(fi)
        self.t_list = t_list

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmGoal(ASTNode):
    _fields = ('t1', 't2')
    __match_args__ = ('fi', 't1', 't2')

    def __init__(self, fi: DebugInfo, t1: ASTNode, t2: ASTNode):
        super().__init__(fi)
        self.t1 = t1
        self.t2 = t2

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmStrat(ASTNode):
    _fields = ('t1', 't2')
    __match_args__ = ('fi', 't1', 't2')

    def __init__(self, fi: DebugInfo, t1: ASTNode, t2: ASTNode):
        super().__init__(fi)
        self.t1 = t1
        self.t2 = t2

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmEv(ASTNode):
    _fields = ('t',)
    __match_args__ = ('fi', 't',)

    def __init__(self, fi: DebugInfo, t: ASTNode):
        super().__init__(fi)
        self.t = t

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmSet(ASTNode):
    _fields = ('t_list',)
    __match_args__ = ('fi', 't_list',)

    def __init__(self, fi: DebugInfo, t_list: list):
        super().__init__(fi)
        self.t_set = []
        for t in t_list:
            if t not in self.t_set:
                self.t_set.append(t)
        # self.t_list = sorted(self.t_set)
        self.t_list = self.t_set

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmMap(ASTNode):
    _fields = ('t1', 't2')
    __match_args__ = ('fi', 't1', 't2')

    def __init__(self, fi: DebugInfo, t1: ASTNode, t2: ASTNode):
        super().__init__(fi)
        self.t1 = t1
        self.t2 = t2

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmRcd(ASTNode):   # aとtのタプルの方が良いかも
    _fields = ('a_list', 't_list')
    __match_args__ = ('fi', 'a_list', 't_list')

    def __init__(self, fi: DebugInfo, a_list: list, t_list: list):
        super().__init__(fi)
        self.a_list = []
        self.t_list = []
        for self.a, self.t in zip(a_list, t_list):
            if self.a in self.a_list:
                self.t_list[self.a_list.index(self.a)] = self.t
            else:
                self.a_list.append(self.a)
                self.t_list.append(self.t)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmRcdAcs(ASTNode):
    _fields = ('t', 'a')
    __match_args__ = ('fi', 't', 'a')

    def __init__(self, fi: DebugInfo, t: ASTNode, a: ASTNode):
        super().__init__(fi)
        self.t = t
        self.a = a

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmLet(ASTNode):
    _fields = ('name', 't1', 't2',)
    __match_args__ = ('fi', 'name', 't1', 't2',)

    def __init__(self, fi: DebugInfo, name: str, t1: ASTNode, t2: ASTNode):
        super().__init__(fi)
        self.name = name
        self.t1 = t1
        self.t2 = t2

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmFuncDef(ASTNode):
    _fields = ('name', 't')
    __match_args__ = ('fi', 'name', 't')

    def __init__(self, fi: DebugInfo, name: str, t: ASTNode):
        super().__init__(fi)
        self.name = name
        self.t = t

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmTrue(ASTNode):
    _fields = ()
    __match_args__ = ('fi', )

    def __init__(self, fi: DebugInfo,):
        super().__init__(fi)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmFalse(ASTNode):
    _fields = ()
    __match_args__ = ('fi', )

    def __init__(self, fi: DebugInfo,):
        super().__init__(fi)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmNot(ASTNode):
    _fields = ('t',)
    __match_args__ = ('fi', 't',)

    def __init__(self, fi: DebugInfo, t: ASTNode):
        super().__init__(fi)
        self.t = t

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmAnd(ASTNode):
    _fields = ('t1', 't2',)
    __match_args__ = ('fi', 't1', 't2',)

    def __init__(self, fi: DebugInfo, t1: ASTNode, t2: ASTNode):
        super().__init__(fi)
        self.t1 = t1
        self.t2 = t2

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmOr(ASTNode):
    _fields = ('t1', 't2',)
    __match_args__ = ('fi', 't1', 't2',)

    def __init__(self, fi: DebugInfo, t1: ASTNode, t2: ASTNode):
        super().__init__(fi)
        self.t1 = t1
        self.t2 = t2

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmXor(ASTNode):
    _fields = ('t1', 't2',)
    __match_args__ = ('fi', 't1', 't2',)

    def __init__(self, fi: DebugInfo, t1: ASTNode, t2: ASTNode):
        super().__init__(fi)
        self.t1 = t1
        self.t2 = t2

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmEq(ASTNode):
    _fields = ('t1', 't2',)
    __match_args__ = ('fi', 't1', 't2',)

    def __init__(self, fi: DebugInfo, t1: ASTNode, t2: ASTNode):
        super().__init__(fi)
        self.t1 = t1
        self.t2 = t2

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmIf(ASTNode):
    _fields = ('t1', 't2', 't3',)
    __match_args__ = ('fi', 't1', 't2', 't3',)

    def __init__(self, fi: DebugInfo, t1: ASTNode, t2: ASTNode, t3: ASTNode):
        super().__init__(fi)
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class TmNull(ASTNode):
    _fields = ()
    __match_args__ = ('fi', )

    def __init__(self, fi: DebugInfo):
        super().__init__(fi)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)
