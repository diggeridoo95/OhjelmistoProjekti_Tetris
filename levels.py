from events import GarbageRows
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
			events=[GarbageRows(2)],
		),
		Level(
			number=3,
			target_score=1500,
			time_limit_seconds=100,
			drop_interval_ms=165,
			events=[GarbageRows(3)],
		),
		Level(
			number=4,
			target_score=1900,
			time_limit_seconds=95,
			drop_interval_ms=150,
			events=[GarbageRows(4, holes_per_row=2)],
		),
		Level(
			number=5,
			target_score=2400,
			time_limit_seconds=90,
			drop_interval_ms=135,
			events=[GarbageRows(5, holes_per_row=2)],
		),

    ]