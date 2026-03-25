from events import GarbageRows, MoleEvent, InvisibilityEvent
from level import Level

def get_levels() -> list[Level]:
    return [
        Level(
            number=1,
            target_score = 700,
            time_limit_seconds = 120,
            drop_interval_ms = 200),

        Level(
			number=2,
			target_score=1100,
			time_limit_seconds=110,
			drop_interval_ms=180,
			events=[
				GarbageRows(2),
				MoleEvent(trigger_chance=0.35, cooldown_ms=10000),
				InvisibilityEvent(trigger_chance=0.002, duration_ms=1000),
			]
		),
		Level(
			number=3,
			target_score=1500,
			time_limit_seconds=100,
			drop_interval_ms=165,
			events=[GarbageRows(3),InvisibilityEvent(trigger_chance=0.0025, duration_ms=1200)],
		),
		Level(
			number=4,
			target_score=1900,
			time_limit_seconds=95,
			drop_interval_ms=150,
			events=[GarbageRows(4, holes_per_row=2), InvisibilityEvent(trigger_chance=0.003, duration_ms=1500)],
		),
		Level(
			number=5,
			target_score=2400,
			time_limit_seconds=90,
			drop_interval_ms=135,
			events=[GarbageRows(5, holes_per_row=2), InvisibilityEvent(trigger_chance=0.0035, duration_ms=1700)],
		),

    ]