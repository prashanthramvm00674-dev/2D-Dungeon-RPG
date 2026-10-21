import sys
import tempfile
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import core.game as game_module
from core.game import Game
from core.save_manager import SaveManager, SettingsManager
from entities.item import HEALTH_POTION


def click(game, position, clicks=1):
    event_data = {"button": 1, "pos": position}
    if clicks > 1:
        event_data["clicks"] = clicks
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data))
    game.handle_events()


def press(game, key, mod=0):
    pygame.event.post(
        pygame.event.Event(pygame.KEYDOWN, {"key": key, "mod": mod})
    )
    game.handle_events()


def main():
    # Keep the integration test independent from the developer's real saves
    # and preferences. In particular, a previously saved fullscreen preference
    # must not change the expected windowed startup state.
    test_data = tempfile.TemporaryDirectory(prefix="dungeon-rpg-ui-test-")
    test_data_path = Path(test_data.name)
    game_module.SettingsManager = lambda: SettingsManager(
        path=test_data_path / "settings.json"
    )
    game_module.SaveManager = lambda: SaveManager(
        path=test_data_path / "save_slot_1.json"
    )

    game = Game()

    # Windowed startup makes screen capture accessible, while both keyboard
    # routes remain available for returning to immersive fullscreen.
    assert not game.fullscreen
    press(game, pygame.K_RETURN, pygame.KMOD_ALT)
    assert game.fullscreen
    press(game, pygame.K_RETURN, pygame.KMOD_ALT)
    assert not game.fullscreen
    press(game, pygame.K_F11)
    assert game.fullscreen
    press(game, pygame.K_F11)
    assert not game.fullscreen

    # Populate the HUD hitboxes first, just like the real first frame.
    game.render()
    assert game.player.inventory.get_item_count(HEALTH_POTION) == 3
    assert game.wave_manager.current_wave == 1
    assert len(game.enemies) == len(game.wave_manager.initial_roster) == 4
    assert game.quest_manager.status == "active"

    # The top-right button opens a pause menu, not the inventory overlay.
    click(game, game.hud.menu_button_rect.center)
    assert game.paused
    assert not game.inventory_ui.visible
    game.render()
    assert {"resume", "restart", "fullscreen", "quit"} <= set(game.pause_menu_buttons)

    # The pause menu itself can enter and exit fullscreen when function keys
    # are unavailable on the user's keyboard.
    click(game, game.pause_menu_buttons["fullscreen"].center)
    assert game.fullscreen
    game.render()
    click(game, game.pause_menu_buttons["fullscreen"].center)
    assert not game.fullscreen
    game.render()

    # Resume is a real clickable action.
    click(game, game.pause_menu_buttons["resume"].center)
    assert not game.paused

    # Restart from the menu restores a fresh three-potion stack and gear.
    game.render()
    click(game, game.hud.menu_button_rect.center)
    assert game.paused
    game.render()
    click(game, game.pause_menu_buttons["restart"].center)
    assert not game.paused
    assert not game.inventory_ui.visible
    assert game.player.inventory.get_item_count(HEALTH_POTION) == 3
    assert game.wave_manager.current_wave == 1
    assert not game.wave_manager.is_victory

    # The numbered HUD slot is connected to the inventory and uses one potion.
    game.render()
    game.player.health = 50
    click(game, game.hud.hotbar_rects[0].center)
    assert game.player.health == 75
    assert game.player.inventory.get_item_count(HEALTH_POTION) == 2

    # I still opens the inventory. Mouse clicks select, then double-click uses.
    press(game, pygame.K_i)
    assert game.inventory_ui.visible
    game.render()
    layout = game.inventory_ui._calculate_layout(game.screen.get_size())
    potion_rect = game.inventory_ui._slot_rect(0, layout)
    game.player.health = 50
    click(game, potion_rect.center)
    assert game.inventory_ui.selected_slot == 0
    assert game.player.health == 50
    assert game.player.inventory.get_item_count(HEALTH_POTION) == 2

    # The second ordinary click activates the potion even if Pygame omits
    # a native "clicks" field from its real mouse event.
    click(game, potion_rect.center)
    assert game.player.health == 75
    assert game.player.inventory.get_item_count(HEALTH_POTION) == 1

    # I closes it too, retaining the user's existing keyboard shortcut.
    press(game, pygame.K_i)
    assert not game.inventory_ui.visible

    # The quest journal is modal, keyboard-accessible, and does not advance time.
    press(game, pygame.K_j)
    assert game.quest_ui.visible
    old_wave_timer = game.wave_manager.spawn_timer
    game.dt = 1.0
    game.update()
    assert game.wave_manager.spawn_timer == old_wave_timer
    game.render()
    press(game, pygame.K_j)
    assert not game.quest_ui.visible

    # The Ashen Warden is placed on connected floor and speaks only at close range.
    spawn_state = (game.player.x, game.player.y, game.player.rect.topleft)
    spawn_tile = (
        game.player.rect.x // game.world.TILE_SIZE,
        game.player.rect.y // game.world.TILE_SIZE,
    )
    npc_tile = (
        game.npc.rect.centerx // game.world.TILE_SIZE,
        game.npc.rect.centery // game.world.TILE_SIZE,
    )
    assert not game.world.collides_with_wall(game.npc.rect)
    assert game.world.find_path(spawn_tile, npc_tile)

    game.player.rect.center = game.npc.rect.center
    game.player.x, game.player.y = game.player.rect.topleft
    assert game.npc.is_in_range(game.player)
    press(game, pygame.K_e)
    assert game.dialogue_ui.visible
    assert game.dialogue_ui.speaker == game.npc.NAME
    dialogue_wave_timer = game.wave_manager.spawn_timer
    game.dt = 1.0
    game.update()
    assert game.wave_manager.spawn_timer == dialogue_wave_timer
    game.render()
    press(game, pygame.K_e)
    assert game.dialogue_ui.visible
    assert game.dialogue_ui.line_index == 1
    press(game, pygame.K_e)
    press(game, pygame.K_e)
    assert not game.dialogue_ui.visible

    # Restore the player before continuing the combat regression checks.
    game.player.x, game.player.y, player_rect_position = spawn_state
    game.player.rect.topleft = player_rect_position

    # A wave ends only after every living enemy is defeated. The next wave
    # waits through its intermission, then queues/spawns reinforcements.
    for enemy in game.enemies:
        if not enemy.is_dead():
            enemy.take_damage(enemy.health + 1)
    game.dt = 0.016
    game.update()
    assert game.wave_manager.is_intermission
    assert game.wave_manager.current_wave == 1

    game.dt = game.wave_manager.intermission_duration + 0.1
    game.update()
    assert game.wave_manager.current_wave == 2
    assert not game.wave_manager.is_intermission
    assert len(game.wave_manager.pending_enemy_types) == 5

    game.dt = 0.016
    game.update()
    assert sum(not enemy.is_dead() for enemy in game.enemies) == 1
    assert len(game.wave_manager.pending_enemy_types) == 4
    spawned_enemy = next(enemy for enemy in game.enemies if not enemy.is_dead())
    assert not game.world.collides_with_wall(spawned_enemy.rect)

    # Restart returns to the four-enemy opening wave and fresh inventory.
    game.restart()
    assert game.wave_manager.current_wave == 1
    assert len(game.enemies) == 4
    assert game.player.inventory.get_item_count(HEALTH_POTION) == 3

    # Victory presentation is renderable and R starts a fresh wave run.
    game.wave_manager.phase = game.wave_manager.VICTORY
    game.quest_manager.update(game.wave_manager, 0, game.player)
    assert game.quest_manager.completed
    assert game.quest_manager.reward_claimed
    assert game.player.xp > 0
    xp_after_reward = game.player.xp
    game.quest_manager.update(game.wave_manager, 0, game.player)
    assert game.player.xp == xp_after_reward
    game.render()
    press(game, pygame.K_r)
    assert game.wave_manager.current_wave == 1
    assert not game.wave_manager.is_victory
    assert len(game.enemies) == 4
    assert game.quest_manager.status == "active"
    assert not game.quest_ui.visible
    assert game.boss is None

    # Clearing the final wave starts a real boss phase instead of declaring
    # victory immediately. The guardian must spawn, take combat damage, and die.
    game.wave_manager.current_wave = game.wave_manager.total_waves
    game.wave_manager.phase = game.wave_manager.ACTIVE
    game.wave_manager.pending_enemy_types = []
    for enemy in game.enemies:
        if not enemy.is_dead():
            enemy.take_damage(enemy.health + 1)

    game.dt = 0.016
    game.update()
    assert game.wave_manager.is_boss
    assert not game.wave_manager.is_victory
    assert game.boss is None

    game.update()
    assert game.boss is not None
    assert not game.boss.is_dead()
    assert not game.world.collides_with_wall(game.boss.rect)
    game.render()

    # Exercise the same boss hit/reward/victory path used by the player's
    # existing attack loop without relying on timing-dependent key presses.
    game.boss.health = game.player.attack_damage
    game.boss.state = "recover"
    game.boss.state_timer = 2.0

    def force_boss_hit(_input_manager, _dt, _world):
        game.player.is_attacking = True
        game.player.attack_has_hit = False
        game.player.attack_rect = game.boss.rect.copy()

    game.player.update = force_boss_hit
    game.update()
    assert game.boss.is_dead()
    assert game.wave_manager.is_victory
    assert game.quest_manager.completed
    assert game.quest_manager.reward_claimed
    assert len(game.loot) >= 1
    game.render()

    press(game, pygame.K_r)
    assert not game.wave_manager.is_boss
    assert not game.wave_manager.is_victory
    assert game.boss is None
    assert game.quest_manager.status == "active"

    pygame.quit()
    test_data.cleanup()
    print(
        "Game UI integration passed: pause menu, inventory/hotbar, dialogue, "
        "waves, boss phase, boss rewards, victory, and restart."
    )


if __name__ == "__main__":
    main()
