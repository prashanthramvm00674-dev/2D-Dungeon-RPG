import sys
from pathlib import Path

import pygame

# Add the project's src directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from world.world import World
from core.camera import Camera
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT


def main():
    pygame.init()

    print("=== Map Expansion Test ===\n")

    world = World()

    # Verify new dimensions
    assert world.columns == 80, f"Expected 80 columns, got {world.columns}"
    assert world.rows == 50, f"Expected 50 rows, got {world.rows}"

    print(f"[PASS] World dimensions: {world.columns}x{world.rows} tiles")

    # Verify pixel dimensions
    expected_width = 80 * 40  # 3200
    expected_height = 50 * 40  # 2000

    assert world.get_width() == expected_width, f"Expected width {expected_width}, got {world.get_width()}"
    assert world.get_height() == expected_height, f"Expected height {expected_height}, got {world.get_height()}"

    print(f"[PASS] World pixel size: {world.get_width()}x{world.get_height()}")

    # Verify world is larger than screen
    assert world.get_width() > SCREEN_WIDTH, "World should be wider than screen"
    assert world.get_height() > SCREEN_HEIGHT, "World should be taller than screen"

    print(f"[PASS] World > Screen: {world.get_width()}x{world.get_height()} > {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    # Count floor and wall tiles
    floor_count = 0
    wall_count = 0

    for row in range(world.rows):
        for column in range(world.columns):
            if world.tiles[row][column] == world.FLOOR:
                floor_count += 1
            elif world.tiles[row][column] == world.WALL:
                wall_count += 1

    print(f"[PASS] Floor tiles: {floor_count}")
    print(f"[PASS] Wall tiles: {wall_count}")

    # Verify there are rooms (not just empty floor)
    assert floor_count > 0, "Should have floor tiles"
    assert wall_count > 0, "Should have wall tiles"

    # Verify moss patches
    assert len(world.moss_patches) > 0, "Should have moss patches"
    print(f"[PASS] Moss patches: {len(world.moss_patches)}")

    # Verify moss patches are on floor tiles
    for patch in world.moss_patches:
        col, row = patch['column'], patch['row']
        width, height = patch['width_tiles'], patch['height_tiles']

        for r in range(row, row + height):
            for c in range(col, col + width):
                assert world.tiles[r][c] == world.FLOOR, \
                    f"Moss patch at ({col}, {row}) should be on floor tiles"

    print("[PASS] All moss patches on valid floor tiles")

    # Test camera with larger world
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Test camera at various positions
    test_positions = [
        (0, 0),
        (world.get_width() // 2, world.get_height() // 2),
        (world.get_width() - 40, world.get_height() - 40),
    ]

    print("\n=== Camera Tests with Larger World ===")
    for x, y in test_positions:
        player_rect = pygame.Rect(x, y, 40, 40)
        camera.update(player_rect, world.get_width(), world.get_height())

        print(f"Player at ({x}, {y}): Camera at ({camera.x}, {camera.y})")

        # Verify camera stays within bounds
        max_x = max(0, world.get_width() - SCREEN_WIDTH)
        max_y = max(0, world.get_height() - SCREEN_HEIGHT)

        assert 0 <= camera.x <= max_x, f"Camera x {camera.x} out of bounds [0, {max_x}]"
        assert 0 <= camera.y <= max_y, f"Camera y {camera.y} out of bounds [0, {max_y}]"

    print("[PASS] Camera clamping works with larger world")

    # Verify camera can move (not stuck at 0,0)
    center_rect = pygame.Rect(world.get_width() // 2, world.get_height() // 2, 40, 40)
    camera.update(center_rect, world.get_width(), world.get_height())

    assert camera.x > 0 or camera.y > 0, "Camera should move from (0,0) with larger world"

    print(f"[PASS] Camera moves: ({camera.x}, {camera.y})")

    # Test collision at various locations
    print("\n=== Collision Tests ===")

    # Find a valid floor tile
    floor_x, floor_y = None, None
    for row in range(1, world.rows - 1):
        for column in range(1, world.columns - 1):
            if world.tiles[row][column] == world.FLOOR:
                floor_x = column * world.TILE_SIZE
                floor_y = row * world.TILE_SIZE
                break
        if floor_x is not None:
            break

    assert floor_x is not None, "Should find at least one floor tile"

    # Test collision in floor area
    floor_rect = pygame.Rect(floor_x, floor_y, 40, 40)
    assert not world.collides_with_wall(floor_rect), "Should not collide with floor"
    print(f"[PASS] Floor collision: no collision at ({floor_x}, {floor_y})")

    # Test collision with wall (edge of map)
    edge_rect = pygame.Rect(0, 0, 40, 40)
    assert world.collides_with_wall(edge_rect), "Should collide with wall at edge"
    print("[PASS] Wall collision: collision detected")

    # Test collision at various points
    collision_tests = [
        (world.get_width() - 20, world.get_height() - 20, True),  # Edge wall
    ]

    for x, y, should_collide in collision_tests:
        test_rect = pygame.Rect(x, y, 40, 40)
        collides = world.collides_with_wall(test_rect)
        assert collides == should_collide, f"Collision at ({x}, {y}) expected {should_collide}, got {collides}"

    print("[PASS] Collision tests passed")

    pygame.quit()
    print("\n=== Map Expansion Test Complete ===")
    print(f"World: {world.columns}x{world.rows} tiles ({world.get_width()}x{world.get_height()}px)")
    print(f"Screen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"Camera can move: YES")
    print(f"Floor tiles: {floor_count}")
    print(f"Wall tiles: {wall_count}")
    print(f"Moss patches: {len(world.moss_patches)}")
    print("All map expansion tests passed!")


if __name__ == "__main__":
    main()
