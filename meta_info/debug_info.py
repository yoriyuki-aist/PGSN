
from attrs import frozen, field
from helpers import helpers

@frozen
class DebugInfo:
    source: str = field(validator=helpers.not_none)
    location: int = field(validator=helpers.not_none)
