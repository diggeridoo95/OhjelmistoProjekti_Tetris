from dataclasses import dataclass, field
from events import LevelEvent

@dataclass
class Level:
    number: int
    target_score: int
    time_limit_seconds: int
    drop_interval_ms: int
    events: list[LevelEvent] = field(default_factory= list)