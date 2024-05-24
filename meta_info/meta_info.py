from attrs import define
from debug_info import DebugInfo


@define
class MetaInfo:
    debug_info: DebugInfo = None

    @classmethod
    def empty(cls):
        cls()
