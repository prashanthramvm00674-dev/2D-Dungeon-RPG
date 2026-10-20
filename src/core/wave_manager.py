"""State machine for the four-wave dungeon survival mode.

The first wave is placed by Game during initialization, preserving the
existing opening encounter. Subsequent waves are spawned gradually through
the callback passed to update().
"""


class WaveManager:
    """Track enemy rosters, controlled spawning, intermissions, and victory."""

    WAVE_ROSTERS = (
        ("Goblin", "Skeleton", "Orc", "Goblin"),
        ("Goblin", "Goblin", "Skeleton", "Skeleton", "Orc"),
        ("Goblin", "Goblin", "Skeleton", "Skeleton", "Orc", "Orc"),
        ("Goblin", "Goblin", "Skeleton", "Skeleton", "Skeleton", "Orc", "Orc"),
    )

    ACTIVE = "active"
    INTERMISSION = "intermission"
    BOSS = "boss"
    VICTORY = "victory"

    MAX_ALIVE_ENEMIES = 5
    SPAWN_INTERVAL = 0.85
    INTERMISSION_DURATION = 3.0
    ANNOUNCEMENT_DURATION = 2.0

    def __init__(
        self,
        wave_rosters=None,
        max_alive_enemies=MAX_ALIVE_ENEMIES,
        spawn_interval=SPAWN_INTERVAL,
        intermission_duration=INTERMISSION_DURATION,
    ):
        rosters = self.WAVE_ROSTERS if wave_rosters is None else wave_rosters
        normalized_rosters = tuple(tuple(roster) for roster in rosters)
        if not normalized_rosters or any(not roster for roster in normalized_rosters):
            raise ValueError("Every wave must contain at least one enemy.")

        self.wave_rosters = normalized_rosters
        self.max_alive_enemies = max(1, int(max_alive_enemies))
        self.spawn_interval = max(0.05, float(spawn_interval))
        self.intermission_duration = max(0.0, float(intermission_duration))

        self.current_wave = 1
        self.phase = self.ACTIVE

        # Game creates the first roster immediately, so no opening enemies
        # remain queued when the manager begins.
        self.pending_enemy_types = []
        self.spawned_this_wave = len(self.wave_rosters[0])
        self.total_spawned = self.spawned_this_wave

        self.spawn_timer = 0.0
        self.intermission_remaining = 0.0
        self.announcement = "WAVE 1"
        self.announcement_timer = self.ANNOUNCEMENT_DURATION

    @property
    def initial_roster(self):
        """The opening roster that Game creates during startup and restart."""
        return self.wave_rosters[0]

    @property
    def total_waves(self):
        return len(self.wave_rosters)

    @property
    def is_victory(self):
        return self.phase == self.VICTORY

    @property
    def is_intermission(self):
        return self.phase == self.INTERMISSION

    @property
    def is_boss(self):
        """Whether the final guardian encounter is active."""
        return self.phase == self.BOSS

    def remaining_count(self, alive_count):
        """Count living, queued enemies and the active guardian, if any."""
        boss_remaining = 1 if self.is_boss else 0
        return (
            max(0, int(alive_count))
            + len(self.pending_enemy_types)
            + boss_remaining
        )

    def defeat_boss(self):
        """Finish the run only when the guardian encounter is active."""
        if not self.is_boss:
            return False

        self.phase = self.VICTORY
        self.announcement = ""
        self.announcement_timer = 0.0
        self.intermission_remaining = 0.0
        return True

    def update(self, dt, alive_count, spawn_enemy):
        """Advance the state machine and spawn at most one queued enemy.

        spawn_enemy receives (enemy_type, spawn_index). Pausing and opening
        inventory are handled by Game returning before calling this method,
        which naturally freezes both spawn and intermission timers.
        """
        dt = max(0.0, float(dt))
        alive_count = max(0, int(alive_count))
        self.announcement_timer = max(0.0, self.announcement_timer - dt)

        if self.phase in (self.BOSS, self.VICTORY):
            return

        if self.phase == self.INTERMISSION:
            self.intermission_remaining = max(
                0.0, self.intermission_remaining - dt
            )
            if self.intermission_remaining <= 0.0:
                self.current_wave += 1
                self.phase = self.ACTIVE
                self.pending_enemy_types = list(
                    self.wave_rosters[self.current_wave - 1]
                )
                self.spawned_this_wave = 0
                self.spawn_timer = 0.0
                self.announcement = f"WAVE {self.current_wave}"
                self.announcement_timer = self.ANNOUNCEMENT_DURATION
            return

        if self.pending_enemy_types:
            if alive_count >= self.max_alive_enemies:
                # Do not bank elapsed time at the cap; killing one enemy must
                # not release a burst of queued enemies immediately.
                self.spawn_timer = self.spawn_interval
            else:
                self.spawn_timer = max(0.0, self.spawn_timer - dt)
                if self.spawn_timer <= 1e-9:
                    enemy_type = self.pending_enemy_types.pop(0)
                    spawn_enemy(enemy_type, self.spawned_this_wave)
                    self.spawned_this_wave += 1
                    self.total_spawned += 1
                    self.spawn_timer = self.spawn_interval
                    alive_count += 1

        if not self.pending_enemy_types and alive_count == 0:
            if self.current_wave >= self.total_waves:
                # The four survival waves are the prelude; the run is not
                # complete until Game confirms the guardian has been defeated.
                self.phase = self.BOSS
                self.announcement = "BOSS ENCOUNTER"
                self.announcement_timer = 3.5
                self.intermission_remaining = 0.0
            else:
                self.phase = self.INTERMISSION
                self.intermission_remaining = self.intermission_duration
                self.announcement = f"WAVE {self.current_wave} CLEARED"
                self.announcement_timer = min(
                    self.ANNOUNCEMENT_DURATION,
                    self.intermission_duration,
                )
