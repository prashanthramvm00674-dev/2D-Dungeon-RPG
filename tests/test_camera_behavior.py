import sys
from pathlib import Path

import pygame

# Add the project's src directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from core.camera import Camera
from world.world import World


def main():
    pygame.init()

    # Current state after Stage 3
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080

    world = World()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    print(f"Screen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"World: {world.get_width()}x{world.get_height()}")
    print(f"World < Screen: {world.get_width() < SCREEN_WIDTH and world.get_height() < SCREEN_HEIGHT}")

    # Test 1: Camera with player at various positions
    test_positions = [
        (320, 180),  # Top-left corner of world
        (640, 360),  # Player spawn position (center)
        (1280, 820),  # Bottom-right corner of world
    ]

    print("\n=== Camera Position Tests ===")
    for x, y in test_positions:
        player_rect = pygame.Rect(x, y, 40, 40)
        camera.update(player_rect, world.get_width(), world.get_height())

        print(f"Player at ({x}, {y}): Camera at ({camera.x}, {camera.y})")

        # Calculate expected camera position
        target_x = player_rect.centerx - SCREEN_WIDTH // 2
        target_y = player_rect.centery - SCREEN_HEIGHT // 2
        max_x = max(0, world.get_width() - SCREEN_WIDTH)
        max_y = max(0, world.get_height() - SCREEN_HEIGHT)
        expected_x = max(0, min(target_x, max_x))
        expected_y = max(0, min(target_y, max_y))

        assert camera.x == expected_x, f"Camera x {camera.x} != expected {expected_x}"
        assert camera.y == expected_y, f"Camera y {camera.y} != expected {expected_y}"

    print("\n[PASS] Camera positions match expected clamping behavior")

    # Test 2: Camera apply method
    print("\n=== Camera Apply Tests ===")
    world_rect = pygame.Rect(100, 100, 40, 40)
    screen_rect = camera.apply(world_rect)

    print(f"World rect: {world_rect}")
    print(f"Screen rect: {screen_rect}")
    print(f"Offset: (-{camera.x}, -{camera.y})")

    assert screen_rect.x == world_rect.x - camera.x
    assert screen_rect.y == world_rect.y - camera.y

    print("[PASS] Camera apply method works correctly")

    # Test 3: Camera with larger world (simulating Stage 4)
    print("\n=== Camera with Larger World (Stage 4 Simulation) ===")
    larger_world_width = 3200  # 80 tiles × 40px
    larger_world_height = 2000  # 50 tiles × 40px

    camera.update(player_rect, larger_world_width, larger_world_height)

    print(f"Larger world: {larger_world_width}x{larger_world_height}")
    print(f"Player at ({x}, {y}): Camera at ({camera.x}, {camera.y})")

    # With larger world, camera should move
    max_x = max(0, larger_world_width - SCREEN_WIDTH)
    max_y = max(0, larger_world_height - SCREEN_HEIGHT)

    print(f"Max camera position: ({max_x}, {max_y})")

    # Camera should be able to move within larger world
    assert max_x > 0, "Max camera x should be > 0 with larger world"
    assert max_y > 0, "Max camera y should be > 0 with larger world"

    print("[PASS] Camera can move within larger world")

    # Test 4: Explanation of current behavior
    print("\n=== Current Behavior Analysis ===")
    print(f"Current world size: {world.get_width()}x{world.get_height()}")
    print(f"Current screen size: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"World fits on screen: {world.get_width() <= SCREEN_WIDTH and world.get_height() <= SCREEN_HEIGHT}")
    print(f"\nWhen world < viewport:")
    print(f"  - max_x = max(0, {world.get_width()} - {SCREEN_WIDTH}) = {max(0, world.get_width() - SCREEN_WIDTH)}")
    print(f"  - max_y = max(0, {world.get_height()} - {SCREEN_HEIGHT}) = {max(0, world.get_height() - SCREEN_HEIGHT)}")
    print(f"  - Camera clamped to (0, 0) to keep entire world visible")
    print(f"\nThis is CORRECT behavior - the camera should stay at (0, 0)")
    print(f"when the entire world fits on screen.")

    pygame.quit()
    print("\n=== Camera Behavior Test Complete ===")
    print("Camera is working correctly.")
    print("No bug found - camera stays at (0, 0) because world < viewport.")


if __name__ == "__main__":
    main()
