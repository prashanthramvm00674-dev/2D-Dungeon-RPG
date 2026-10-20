"""Tests for the main dungeon quest and one-time completion reward."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from core.quest_manager import QuestManager


class FakePlayer:
    def __init__(self):
        self.is_dead = False
        self.xp_awarded = 0

    def add_xp(self, amount):
        self.xp_awarded += amount


class FakeWaves:
    def __init__(self):
        self.current_wave = 1
        self.total_waves = 4
        self.is_victory = False

    def remaining_count(self, alive_count):
        return max(0, alive_count) + 3


def test_quest_stays_active_until_victory():
    quest = QuestManager()
    waves = FakeWaves()
    player = FakePlayer()

    assert quest.status == "active"
    assert not quest.update(waves, 2, player)
    assert player.xp_awarded == 0
    assert not quest.completed


def test_quest_awards_xp_once_on_victory():
    quest = QuestManager()
    waves = FakeWaves()
    player = FakePlayer()
    waves.current_wave = 4
    waves.is_victory = True

    assert quest.update(waves, 0, player)
    assert quest.completed
    assert quest.reward_claimed
    assert player.xp_awarded == QuestManager.REWARD_XP
    assert not quest.update(waves, 0, player)
    assert player.xp_awarded == QuestManager.REWARD_XP


def test_player_death_does_not_complete_quest():
    quest = QuestManager()
    waves = FakeWaves()
    player = FakePlayer()
    waves.is_victory = True
    player.is_dead = True

    assert not quest.update(waves, 0, player)
    assert not quest.completed
    assert player.xp_awarded == 0


def test_progress_includes_queued_enemies_and_reward():
    quest = QuestManager()
    waves = FakeWaves()
    snapshot = quest.progress(waves, 2)

    assert snapshot["name"] == "THE DUNGEON PURGE"
    assert snapshot["current_wave"] == 1
    assert snapshot["total_waves"] == 4
    assert snapshot["enemies_remaining"] == 5
    assert snapshot["reward_xp"] == 50
    assert not snapshot["completed"]


def main():
    test_quest_stays_active_until_victory()
    test_quest_awards_xp_once_on_victory()
    test_player_death_does_not_complete_quest()
    test_progress_includes_queued_enemies_and_reward()
    print("Quest manager tests passed: progression, death handling, and one-time reward.")


if __name__ == "__main__":
    main()
