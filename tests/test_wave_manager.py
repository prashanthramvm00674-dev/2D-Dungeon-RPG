"""Unit tests for the four-wave survival state machine."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from core.wave_manager import WaveManager


def test_rosters_and_opening_state():
    manager = WaveManager()
    assert manager.total_waves == 4
    assert manager.current_wave == 1
    assert manager.phase == WaveManager.ACTIVE
    assert manager.initial_roster == ("Goblin", "Skeleton", "Orc", "Goblin")
    assert len(manager.wave_rosters[1]) == 5
    assert len(manager.wave_rosters[2]) == 6
    assert len(manager.wave_rosters[3]) == 7
    assert manager.remaining_count(4) == 4


def test_wave_waits_for_living_and_queued_enemies():
    manager = WaveManager(
        wave_rosters=(("Goblin", "Skeleton"), ("Orc", "Goblin", "Skeleton")),
        max_alive_enemies=2,
        spawn_interval=0.5,
        intermission_duration=1.0,
    )
    spawned = []
    spawn = lambda kind, index: spawned.append((kind, index))

    manager.update(0.1, 0, spawn)
    assert manager.is_intermission
    assert manager.current_wave == 1
    assert not spawned

    manager.update(0.5, 0, spawn)
    assert manager.is_intermission
    manager.update(0.5, 0, spawn)
    assert manager.phase == WaveManager.ACTIVE
    assert manager.current_wave == 2
    assert manager.remaining_count(0) == 3

    manager.update(0.5, 0, spawn)
    assert spawned == [("Orc", 0)]
    assert manager.remaining_count(1) == 3

    # Reaching the cap blocks spawns; the next enemy does not burst in.
    manager.update(10.0, 2, spawn)
    assert len(spawned) == 1
    manager.update(0.49, 1, spawn)
    assert len(spawned) == 1
    manager.update(0.01, 1, spawn)
    assert len(spawned) == 2
    assert spawned[1] == ("Goblin", 1)


def test_queued_enemies_count_as_remaining():
    manager = WaveManager()
    manager.current_wave = 2
    manager.pending_enemy_types = ["Goblin", "Orc", "Skeleton"]
    assert manager.remaining_count(2) == 5


def test_final_wave_starts_boss_and_requires_guardian_defeat():
    manager = WaveManager(wave_rosters=(("Goblin",),))
    manager.update(0.016, 0, lambda kind, index: None)
    assert manager.is_boss
    assert manager.phase == WaveManager.BOSS
    assert not manager.is_victory
    assert manager.remaining_count(0) == 1
    assert not manager.defeat_boss() is False
    assert manager.is_victory
    assert manager.phase == WaveManager.VICTORY
    assert manager.remaining_count(0) == 0


def test_each_spawn_callback_receives_progressive_index():
    manager = WaveManager(
        wave_rosters=(("Goblin",), ("Goblin", "Skeleton", "Orc")),
        max_alive_enemies=5,
        spawn_interval=0.05,
        intermission_duration=0,
    )
    spawned = []
    spawn = lambda kind, index: spawned.append((kind, index))
    manager.update(0.01, 0, spawn)  # Finish the one-enemy first wave.
    manager.update(0.01, 0, spawn)  # Enter wave 2.
    manager.update(0.05, 0, spawn)
    manager.update(0.05, 0, spawn)
    manager.update(0.05, 0, spawn)
    assert [index for _, index in spawned] == [0, 1, 2]
    assert [kind for kind, _ in spawned] == ["Goblin", "Skeleton", "Orc"]


def main():
    test_rosters_and_opening_state()
    test_wave_waits_for_living_and_queued_enemies()
    test_queued_enemies_count_as_remaining()
    test_final_wave_starts_boss_and_requires_guardian_defeat()
    test_each_spawn_callback_receives_progressive_index()
    print(
        "Wave manager tests passed: rosters, spawn cap, timing, transitions, "
        "queue counts, spawn indices, boss gating, and victory."
    )


if __name__ == "__main__":
    main()
