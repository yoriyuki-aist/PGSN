class DebugInfo:    # デバッグ情報に関するクラス
    __match_args__ = ('source', 'location',)

    def __init__(self, source: str = '', location: int = 0):    # ソースコードの原文と位置情報を持つ
        self.source = source
        self.location = location

    def __repr__(self):
        # return ''
        return (self.source, self.location) 

    def __str__(self):
        return f'source:{self.source}\nlocation:{self.location}'

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)
