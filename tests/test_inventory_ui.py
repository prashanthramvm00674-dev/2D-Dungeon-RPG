import sys
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from entities.item import HEALTH_POTION, IRON_SWORD, SHIELD
from entities.player import Player
from ui.inventory_ui import InventoryUI
from ui.hud import HUD


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))

    player = Player()
    inventory = player.inventory
    assert inventory.add_item(HEALTH_POTION, 3)
    assert inventory.add_item(IRON_SWORD, 1)
    assert inventory.add_item(SHIELD, 1)

    ui = InventoryUI()
    ui.toggle()
    layout = ui._calculate_layout(screen.get_size())
    potion_rect = ui._slot_rect(0, layout)

    # Clicking a visible slot reliably selects it without consuming anything.
    assert ui.handle_click(
        potion_rect.center,
        inventory,
        player,
        screen.get_size()
    )
    assert ui.selected_slot == 0
    assert inventory.get_item_count(HEALTH_POTION) == 3
    assert player.health == player.max_health

    # The action button remains a clear single-click path to use a potion.
    player.health = 50
    assert ui.handle_click(
        layout["button_rect"].center,
        inventory,
        player,
        screen.get_size()
    )
    assert player.health == 75
    assert inventory.get_item_count(HEALTH_POTION) == 2

    # Double-clicking an item also activates it, using the same item action.
    player.health = 50
    assert ui.handle_click(
        potion_rect.center,
        inventory,
        player,
        screen.get_size(),
        click_count=2
    )
    assert player.health == 75
    assert inventory.get_item_count(HEALTH_POTION) == 1

    # Single-clicking gear selects it; clicking EQUIP equips it.
    sword_rect = ui._slot_rect(1, layout)
    ui.handle_click(sword_rect.center, inventory, player, screen.get_size())
    assert ui.selected_slot == 1
    assert player.equipped_weapon is None
    ui.handle_click(
        layout["button_rect"].center,
        inventory,
        player,
        screen.get_size()
    )
    assert player.equipped_weapon == IRON_SWORD

    # I continues to close/reopen the inventory through keyboard controls.
    ui.handle_key(pygame.K_i, inventory, player)
    assert not ui.visible
    ui.toggle()
    assert ui.visible

    # The HUD's populated hotbar still has reliable click targets.
    hud = HUD()
    hud.render(screen, player, [], inventory)
    assert len(hud.hotbar_rects) == 5
    assert hud.hotbar_slot_at(hud.hotbar_rects[0].center) == 0
    assert hud.hotbar_slot_at(hud.hotbar_rects[4].center) == 4
    assert hud.hotbar_slot_at((0, 0)) is None

    # Inventory and redesigned grayscale enemy emblem render without errors.
    ui.render(screen, inventory, player)
    pygame.quit()
    print(
        "Inventory checks passed: mouse selection, double-click activation, "
        "action buttons, I-key controls, gear, hotbar, and HUD rendering."
    )


if __name__ == "__main__":
    main()
