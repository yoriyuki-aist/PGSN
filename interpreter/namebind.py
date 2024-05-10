from . pgsn_ast import ASTNode

class Binding:
    def __init__(self, namebind: ASTNode):
        self.namebind = namebind

    def __repr__(self):
        return self.namebind

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)


class Context:
    def __init__(self, name: str, bind: Binding):
        self.name = name
        self.bind = bind

    def __repr__(self) -> str:
        return (self.name, self.bind)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)
