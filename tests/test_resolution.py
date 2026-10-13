import sys
from pathlib import Path

import pygame

# Add the project's src directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from world.world import World
from core.camera import Camera
from ui.hud import HUD


def main():
    pygame.init()

    # Verify settings match target resolution
    assert SCREEN_WIDTH == 1920, f"SCREEN_WIDTH should be 1920, got {SCREEN_WIDTH}"
    assert SCREEN_HEIGHT == 1080, f"SCREEN_HEIGHT should be 1080, got {SCREEN_HEIGHT}"
    assert FPS == 60, f"FPS should be 60, got {FPS}"

    print(f"[PASS] Settings verified: {SCREEN_WIDTH}x{SCREEN_HEIGHT} @ {FPS} FPS")

    # Test window creation with new resolution
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Resolution Test")

    assert screen.get_width() == SCREEN_WIDTH, f"Screen width should be {SCREEN_WIDTH}"
    assert screen.get_height() == SCREEN_HEIGHT, f"Screen height should be {SCREEN_HEIGHT}"

    print(f"[PASS] Window created at {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    # Test World with new resolution
    world = World()
    assert world.get_width() == 3200, "World width should be 3200 (80 × 40)"
    assert world.get_height() == 2000, "World height should be 2000 (50 × 40)"

    print(f"[PASS] World dimensions: {world.get_width()}x{world.get_height()}")

    # Test Camera with new resolution
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    assert camera.screen_width == SCREEN_WIDTH, f"Camera width should be {SCREEN_WIDTH}"
    assert camera.screen_height == SCREEN_HEIGHT, f"Camera height should be {SCREEN_HEIGHT}"

    print(f"[PASS] Camera initialized: {camera.screen_width}x{camera.screen_height}")

    # Test camera clamping with new resolution
    # Position camera at various locations and verify it stays within bounds
    test_positions = [
        (0, 0),  # Top-left corner
        (world.get_width() // 2, world.get_height() // 2),  # Center
        (world.get_width(), world.get_height()),  # Bottom-right corner
    ]

    for x, y in test_positions:
        test_rect = pygame.Rect(x, y, 40, 40)
        camera.update(test_rect, world.get_width(), world.get_height())

        # Verify camera stays within world bounds
        max_x = max(0, world.get_width() - SCREEN_WIDTH)
        max_y = max(0, world.get_height() - SCREEN_HEIGHT)

        assert 0 <= camera.x <= max_x, f"Camera x {camera.x} out of bounds [0, {max_x}]"
        assert 0 <= camera.y <= max_y, f"Camera y {camera.y} out of bounds [0, {max_y}]"

    print(f"[PASS] Camera clamping verified at multiple positions")

    # Test HUD with new resolution
    hud = HUD()
    print(f"[PASS] HUD initialized")

    # Test rendering with new resolution (world only, HUD requires player)
    screen.fill((20, 20, 25))
    world.render(screen, camera)

    print(f"[PASS] Rendering successful at {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    # Test texture generation still works
    from graphics.dungeon_textures import DungeonTextures
    textures = DungeonTextures()

    floor_tile = textures.get_floor_tile(0)
    assert floor_tile.get_size() == (40, 40), "Floor tile should still be 40x40"

    wall_tile = textures.get_wall_tile(0)
    assert wall_tile.get_size() == (40, 40), "Wall tile should still be 40x40"

    print(f"[PASS] Textures still generate correctly")

    pygame.quit()
    print("\n=== Resolution Test Complete ===")
    print(f"Target: 1920x1080")
    print(f"Actual: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"World: {world.get_width()}x{world.get_height()}")
    print(f"Camera: {camera.screen_width}x{camera.screen_height}")
    print("All resolution tests passed!")


if __name__ == "__main__":
    main()
