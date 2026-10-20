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


def press(game, key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": key}))
    game.handle_events()


def main():
    game = Game()

    # Populate the HUD hitboxes first, just like the real first frame.
    game.render()
    assert game.player.inventory.get_item_count(HEALTH_POTION) == 3

    # The top-right button opens a pause menu, not the inventory overlay.
    click(game, game.hud.menu_button_rect.center)
    assert game.paused
    assert not game.inventory_ui.visible
    game.render()
    assert {"resume", "restart", "quit"} <= set(game.pause_menu_buttons)

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

    click(game, potion_rect.center, clicks=2)
    assert game.player.health == 75
    assert game.player.inventory.get_item_count(HEALTH_POTION) == 1

    # I closes it too, retaining the user's existing keyboard shortcut.
    press(game, pygame.K_i)
    assert not game.inventory_ui.visible

    pygame.quit()
    print(
        "Game UI integration passed: pause menu, restart, hotbar, mouse "
        "inventory selection/double-click use, and I-key toggle."
    )


if __name__ == "__main__":
    main()
