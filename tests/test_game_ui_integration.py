import sys
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from core.game import Game
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

    pygame.quit()
    print(
        "Game UI integration passed: pause menu, restart, hotbar, mouse "
        "inventory selection/double-click use, and I-key toggle."
    )


if __name__ == "__main__":
    main()
