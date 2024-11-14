from debug_info import DebugInfo
from attrs import field, frozen


@frozen
class MetaInfo:
    debug_info: DebugInfo = field(default=None)
    name_info: str = field(default=None)


empty = MetaInfo()

