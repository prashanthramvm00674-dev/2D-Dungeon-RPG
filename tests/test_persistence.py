"""Regression tests for atomic save files and persistent game state/settings."""

import json
import sys
import tempfile
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from core.game import Game
from core.save_manager import (
    DEFAULT_SETTINGS,
    SAVE_SCHEMA_VERSION,
    SETTINGS_SCHEMA_VERSION,
    SaveManager,
    SettingsManager,
)
from entities.dungeon_boss import DungeonBoss
from entities.item import HEALTH_POTION, IRON_SWORD
from entities.loot import Loot
from core.wave_manager import WaveManager


def test_save_manager_atomic_round_trip_and_validation():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "save.json"
        manager = SaveManager(path)
        payload = {
            "schema_version": SAVE_SCHEMA_VERSION,
            "saved_at": "2026-10-21T00:00:00+00:00",
            "game": {"player": {"health": 77}},
        }

        assert manager.save(payload)
        assert manager.exists()
        assert manager.load() == payload
        assert not list(Path(directory).glob("*.tmp"))
        assert not list(Path(directory).glob(".*.tmp"))

        assert not manager.save({"schema_version": 999, "game": {}})
        assert manager.load() == payload

        path.write_text("{broken json", encoding="utf-8")
        assert manager.load() is None
        assert "could not be read" in manager.last_error


def test_settings_persist_and_recover_from_corruption():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "settings.json"
        manager = SettingsManager(path)

        assert manager.load() == DEFAULT_SETTINGS
        assert manager.set("lighting_enabled", False)
        assert manager.set("post_processing_enabled", False)
        assert manager.set("start_fullscreen", True)

        reloaded = SettingsManager(path)
        settings = reloaded.load()
        assert settings["lighting_enabled"] is False
        assert settings["post_processing_enabled"] is False
        assert settings["start_fullscreen"] is True
        assert settings["autosave_on_quit"] is True

        path.write_text(
            json.dumps({
                "schema_version": SETTINGS_SCHEMA_VERSION,
                "settings": {"lighting_enabled": "off"},
            }),
            encoding="utf-8",
        )
        recovered = SettingsManager(path)
        assert recovered.load() == DEFAULT_SETTINGS
        assert recovered.last_error


def test_game_state_round_trip_including_boss_and_inventory():
    with tempfile.TemporaryDirectory() as directory:
        pygame.init()
        game = Game()
        game.save_manager = SaveManager(Path(directory) / "slot.json")

        game.player.health = 37
        game.player.level = 3
        game.player.xp = 24
        game.player.xp_to_next_level = 225
        game.player.inventory.add_item(HEALTH_POTION, 2)
        game.player.equipped_weapon = IRON_SWORD
        game.player.recalculate_attack_damage()

        game.wave_manager.current_wave = 4
        game.wave_manager.phase = WaveManager.INTERMISSION
        game.wave_manager.intermission_remaining = 0.0
        game.wave_manager.spawn_timer = 0.4
        game.wave_manager.announcement = "BOSS ENCOUNTER"
        game.wave_manager.announcement_timer = 0.7

        enemy = game.enemies[0]
        enemy.health = 17
        enemy.attack_timer = 0.6
        game.loot.append(Loot(enemy.rect.x + 80, enemy.rect.y + 80, HEALTH_POTION))

        # Exercise boss persistence too; reloading should preserve telegraph
        # timing and target lock rather than silently granting a free attack.
        position = game.world.get_edge_spawn_positions(1)[0]
        game.boss = DungeonBoss(*position)
        game.boss.health = game.boss.max_health // 2
        game.boss.state = "pulse_windup"
        game.boss.state_timer = 0.55
        game.boss.special_cooldown = 3.0
        game.boss.telegraph_position = (
            game.player.rect.centerx + 20,
            game.player.rect.centery + 25,
        )
        game.wave_manager.phase = WaveManager.BOSS

        assert game.save_game()
        saved_player_position = game.player.rect.topleft

        game.player.health = 1
        game.player.inventory.clear()
        game.enemies.clear()
        game.boss = None
        game.loot.clear()
        game.wave_manager.phase = WaveManager.ACTIVE
        game.wave_manager.current_wave = 1

        assert game.load_game()
        assert game.player.health == 37
        assert game.player.level == 3
        assert game.player.xp == 24
        assert game.player.rect.topleft == saved_player_position
        assert game.player.inventory.get_item_count(HEALTH_POTION) == 5
        assert game.player.equipped_weapon == IRON_SWORD
        assert game.wave_manager.is_boss
        assert game.wave_manager.current_wave == 4
        assert len(game.enemies) == 4
        assert game.enemies[0].health == 17
        assert game.enemies[0].attack_timer == 0.6
        assert len(game.loot) == 1
        assert game.boss is not None
        assert game.boss.health == game.boss.max_health // 2
        assert game.boss.state == "pulse_windup"
        assert game.boss.state_timer == 0.55
        assert game.boss.telegraph_position == (
            game.player.rect.centerx + 20,
            game.player.rect.centery + 25,
        )
        assert not game.paused
        assert not game.inventory_ui.visible
        assert not game.quest_ui.visible

        pygame.quit()


def test_invalid_game_payload_does_not_mutate_live_state():
    with tempfile.TemporaryDirectory() as directory:
        pygame.init()
        game = Game()
        game.save_manager = SaveManager(Path(directory) / "slot.json")
        original_health = game.player.health
        payload = {
            "schema_version": SAVE_SCHEMA_VERSION,
            "saved_at": "bad but harmless",
            "game": {"player": []},
        }
        assert game.save_manager.save(payload)
        assert not game.load_game()
        assert game.player.health == original_health
        assert "failed" in game.persistence_status.lower()
        pygame.quit()


def main():
    test_save_manager_atomic_round_trip_and_validation()
    test_settings_persist_and_recover_from_corruption()
    test_game_state_round_trip_including_boss_and_inventory()
    test_invalid_game_payload_does_not_mutate_live_state()
    print(
        "Persistence tests passed: atomic saves, corrupt-file recovery, "
        "settings, full run round-trip, and safe rejection of invalid state."
    )


if __name__ == "__main__":
    main()
