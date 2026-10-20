"""Small, testable quest progression for the dungeon survival run."""


class QuestManager:
    """Track the main dungeon quest and grant its completion reward once."""

    QUEST_ID = "dungeon_purge"
    QUEST_NAME = "THE DUNGEON PURGE"
    DESCRIPTION = "Defeat every enemy across all four waves."
    REWARD_XP = 50

    def __init__(self):
        self.completed = False
        self.reward_claimed = False

    @property
    def status(self):
        return "completed" if self.completed else "active"

    def update(self, wave_manager, alive_count, player):
        """Complete the quest only when the run is won, never on player death."""
        if self.completed or player.is_dead or not wave_manager.is_victory:
            return False

        self.completed = True
        if not self.reward_claimed:
            player.add_xp(self.REWARD_XP)
            self.reward_claimed = True
        return True

    def progress(self, wave_manager, alive_count):
        """Return a display-ready snapshot without mutating quest state."""
        remaining = wave_manager.remaining_count(alive_count)
        return {
            "name": self.QUEST_NAME,
            "description": self.DESCRIPTION,
            "status": self.status,
            "current_wave": min(wave_manager.current_wave, wave_manager.total_waves),
            "total_waves": wave_manager.total_waves,
            "enemies_remaining": remaining,
            "reward_xp": self.REWARD_XP,
            "completed": self.completed,
        }
