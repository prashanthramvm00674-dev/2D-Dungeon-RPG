import sys
from pathlib import Path

import pygame

# Add the project's src directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from core.game import Game


def main():
    pygame.init()

    print("=== Rendering Debug ===\n")

    print(f"Configured resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    game = Game()

    print(f"Game screen size: {game.screen.get_width()}x{game.screen.get_height()}")
    print(f"Game screen surface: {game.screen.get_size()}")

    print(f"\nWorld size: {game.world.get_width()}x{game.world.get_height()}")
    print(f"Camera screen width: {game.camera.screen_width}")
    print(f"Camera screen height: {game.camera.screen_height}")

    print(f"\nPlayer position: ({game.player.x}, {game.player.y})")
    print(f"Player rect: {game.player.rect}")

    print(f"\nCamera position: ({game.camera.x}, {game.camera.y})")

    # Test HUD rendering
    print(f"\n=== HUD Test ===")
    hud = game.hud
    hud.render(game.screen, game.player, game.enemies)
    print("HUD rendered successfully")

    # Test Inventory UI rendering (when visible)
    print(f"\n=== Inventory UI Test ===")
    game.inventory_ui.visible = True
    game.inventory_ui.render(game.screen, game.player.inventory, game.player)
    print("Inventory UI rendered successfully")
    game.inventory_ui.visible = False

    # Save a test render
    game.render()
    screenshot_path = PROJECT_ROOT / "tests" / "rendering_debug.png"
    pygame.image.save(game.screen, str(screenshot_path))
    print(f"\nDebug render saved to: {screenshot_path}")

    pygame.quit()


if __name__ == "__main__":
    main()
