from events import GarbageRows, MoleEvent, InvisibilityEvent, InversionEvent
from level import Level

def get_levels() -> list[Level]:
    return [
        Level(
            number=1,
            target_score=1000,
            time_limit_seconds=120,
            drop_interval_ms=300,
            global_event_cooldown_ms=3000,
            events=[
            	InvisibilityEvent(trigger_chance=0.002, duration_ms=1200),
                InversionEvent(trigger_chance = 0.07, lock_target = 1),
			],
		),
        Level(
			number=2,
			target_score=1200,
			time_limit_seconds=110,
			drop_interval_ms=275,
            global_event_cooldown_ms=2900,
			events=[
				GarbageRows(2),
				MoleEvent(trigger_chance=0.25),
				InvisibilityEvent(trigger_chance=0.003, duration_ms=1250),
                InversionEvent(trigger_chance = 0.08, lock_target = 2),
			],
		),
		Level(
			number=3,
			target_score=1400,
			time_limit_seconds=100,
			drop_interval_ms=250,
            global_event_cooldown_ms=2800,
			events=[
                GarbageRows(3),
                MoleEvent(trigger_chance=0.35),
                InvisibilityEvent(trigger_chance=0.004, duration_ms=1300),
                InversionEvent(trigger_chance = 0.09, lock_target = 3),
            ],
		),
		Level(
			number=4,
			target_score=1600,
			time_limit_seconds=95,
			drop_interval_ms=225,
            global_event_cooldown_ms=2700,
			events=[
                GarbageRows(4, holes_per_row=2),
                MoleEvent(trigger_chance=0.45),
                InvisibilityEvent(trigger_chance=0.005, duration_ms=1350),
                InversionEvent(trigger_chance = 0.1, lock_target = 4),
            ],
		),
		Level(
			number=5,
			target_score=1800,
			time_limit_seconds=90,
			drop_interval_ms=200,
            global_event_cooldown_ms=2600,
			events=[
                GarbageRows(5, holes_per_row=2),
                MoleEvent(trigger_chance=0.55),
                InvisibilityEvent(trigger_chance=0.006, duration_ms=1400),
                InversionEvent(trigger_chance = 0.15, lock_target = 4),
            ],
		),

    ]