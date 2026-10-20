import sys
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from entities.inventory import Inventory
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

    # Clicking an item only selects it; it must not use a potion or equip gear.
    potion_rect = pygame.Rect(
        layout["slot_start_x"],
        layout["slot_start_y"],
        layout["slot_size"],
        layout["slot_size"]
    )
    ui.handle_click(
        potion_rect.center,
        inventory,
        player,
        screen.get_size()
    )
    assert ui.selected_slot == 0
    assert inventory.get_item_count(HEALTH_POTION) == 3
    assert player.health == player.max_health

    # Using the explicit action button consumes exactly one potion and heals.
    player.health = 50
    ui.handle_click(
        layout["button_rect"].center,
        inventory,
        player,
        screen.get_size()
    )
    assert player.health == 75
    assert inventory.get_item_count(HEALTH_POTION) == 2

    # Gear also requires explicit selection and action instead of toggling
    # merely because its slot was clicked.
    sword_rect = pygame.Rect(
        layout["slot_start_x"] + layout["slot_size"] + layout["gap"],
        layout["slot_start_y"],
        layout["slot_size"],
        layout["slot_size"]
    )
    ui.handle_click(sword_rect.center, inventory, player, screen.get_size())
    assert player.equipped_weapon is None
    ui.handle_click(
        layout["button_rect"].center,
        inventory,
        player,
        screen.get_size()
    )
    assert player.equipped_weapon == IRON_SWORD

    # A populated inventory appears in the hotbar and maintains reliable
    # click targets for each quick slot.
    hud = HUD()
    hud.render(screen, player, [], inventory)
    assert len(hud.hotbar_rects) == 5
    assert hud.hotbar_slot_at(hud.hotbar_rects[0].center) == 0
    assert hud.hotbar_slot_at(hud.hotbar_rects[4].center) == 4
    assert hud.hotbar_slot_at((0, 0)) is None

    # The inventory UI is a real render target as well as working data.
    ui.render(screen, inventory, player)

    pygame.quit()
    print(
        "Inventory checks passed: selection is safe, potions use explicitly, "
        "gear equips explicitly, and hotbar slots are connected."
    )


if __name__ == "__main__":
    main()
