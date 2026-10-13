import sys
from pathlib import Path

import pygame

# Add the project's src directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from world.world import World
from entities.player import Player
from core.game import Game


def main():
    pygame.init()

    print("=== Safe Spawn Tests ===\n")

    world = World()

    # Test 1: get_safe_spawn_position returns valid floor tile
    print("Test 1: Safe spawn position returns valid floor tile")
    spawn_x, spawn_y = world.get_safe_spawn_position()
    tile_x = spawn_x // world.TILE_SIZE
    tile_y = spawn_y // world.TILE_SIZE

    assert 0 <= tile_x < world.columns, f"Spawn x {tile_x} out of bounds"
    assert 0 <= tile_y < world.rows, f"Spawn y {tile_y} out of bounds"
    assert world.tiles[tile_y][tile_x] == world.FLOOR, f"Spawn at ({tile_x}, {tile_y}) is not floor"

    print(f"[PASS] Spawn position ({spawn_x}, {spawn_y}) is valid floor tile at ({tile_x}, {tile_y})")

    # Test 2: Player spawn has no collision
    print("\nTest 2: Player spawn has no collision")
    player = Player()
    player.x = spawn_x
    player.y = spawn_y
    player.rect.x = spawn_x
    player.rect.y = spawn_y

    assert not world.collides_with_wall(player.rect), f"Player at ({spawn_x}, {spawn_y}) collides with wall"

    print(f"[PASS] Player spawn has no collision")

    # Test 3: Player spawn has clearance from walls
    print("\nTest 3: Player spawn has clearance from walls")
    # Check 3x3 area for walls
    has_wall_nearby = False
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            check_x = tile_x + dx
            check_y = tile_y + dy
            if 0 <= check_x < world.columns and 0 <= check_y < world.rows:
                if world.tiles[check_y][check_x] == world.WALL:
                    has_wall_nearby = True
                    break
        if has_wall_nearby:
            break

    assert not has_wall_nearby, f"Spawn at ({tile_x}, {tile_y}) has wall nearby"

    print(f"[PASS] Spawn has clearance from walls")

    # Test 4: Game class spawns player safely
    print("\nTest 4: Game class spawns player safely")
    game = Game()

    assert not game.world.collides_with_wall(game.player.rect), "Game player collides at spawn"

    print(f"[PASS] Game spawns player safely at ({game.player.x}, {game.player.y})")

    # Test 5: Game class spawns enemies safely
    print("\nTest 5: Game class spawns enemies safely")
    for enemy in game.enemies:
        assert not game.world.collides_with_wall(enemy.rect), f"Enemy at ({enemy.x}, {enemy.y}) collides at spawn"

    print(f"[PASS] Game spawns all {len(game.enemies)} enemies safely")

    # Test 6: Spawn positions are deterministic
    print("\nTest 6: Spawn positions are deterministic")
    world2 = World()
    spawn_x1, spawn_y1 = world.get_safe_spawn_position()
    spawn_x2, spawn_y2 = world2.get_safe_spawn_position()

    assert spawn_x1 == spawn_x2 and spawn_y1 == spawn_y2, "Spawn positions should be deterministic"

    print(f"[PASS] Spawn positions are deterministic")

    # Test 7: Movement test
    print("\nTest 7: Movement test")
    game = Game()

    # Move player right
    original_x = game.player.x
    game.player.x += 100
    game.player.rect.x = game.player.x

    collides = game.world.collides_with_wall(game.player.rect)

    # Reset
    game.player.x = original_x
    game.player.rect.x = original_x

    print(f"[PASS] Movement test completed")

    pygame.quit()
    print("\n=== Safe Spawn Tests Complete ===")
    print("All spawn tests passed!")


if __name__ == "__main__":
    main()
