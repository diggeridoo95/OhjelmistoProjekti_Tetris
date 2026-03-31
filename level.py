from dataclasses import dataclass, field
from events import LevelEvent

@dataclass
class Level:
    number: int
    target_score: int
    time_limit_seconds: int
    drop_interval_ms: int
    global_event_cooldown_ms: int = 2500
    events: list[LevelEvent] = field(default_factory= list)