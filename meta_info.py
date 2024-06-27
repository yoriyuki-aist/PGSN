from attrs import define
from debug_info import DebugInfo
from attrs import field, frozen, evolve, define


@frozen
class MetaInfo:
    debug_info: DebugInfo = None
    name_info: str = None

