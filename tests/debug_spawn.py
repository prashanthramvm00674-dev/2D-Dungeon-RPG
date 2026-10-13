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

    print("=== Player Spawn Investigation ===\n")

    world = World()
    player = Player()

    # Test safe spawn position
    spawn_x, spawn_y = world.get_safe_spawn_position()
    player.x = spawn_x
    player.y = spawn_y
    player.rect.x = spawn_x
    player.rect.y = spawn_y

    print(f"Player spawn position: ({player.x}, {player.y})")
    print(f"Player size: {player.width}x{player.height}")
    print(f"Player rect: {player.rect}")

    # Calculate tile coordinates
    tile_x = player.x // world.TILE_SIZE
    tile_y = player.y // world.TILE_SIZE

    print(f"\nPlayer tile coordinates: ({tile_x}, {tile_y})")
    print(f"World dimensions: {world.columns}x{world.rows} tiles")

    # Check tile type at player position
    if 0 <= tile_x < world.columns and 0 <= tile_y < world.rows:
        tile_type = world.tiles[tile_y][tile_x]
        tile_name = "FLOOR" if tile_type == world.FLOOR else "WALL"
        print(f"Tile at ({tile_x}, {tile_y}): {tile_name}")
    else:
        print(f"Tile at ({tile_x}, {tile_y}): OUT OF BOUNDS")

    # Check all tiles covered by player collision rectangle
    print(f"\n=== Collision Rectangle Coverage ===")
    player_rect = player.rect

    left = player_rect.left // world.TILE_SIZE
    right = (player_rect.right - 1) // world.TILE_SIZE
    top = player_rect.top // world.TILE_SIZE
    bottom = (player_rect.bottom - 1) // world.TILE_SIZE

    print(f"Player rect covers tiles: columns {left}-{right}, rows {top}-{bottom}")

    for row in range(top, bottom + 1):
        for column in range(left, right + 1):
            if 0 <= column < world.columns and 0 <= row < world.rows:
                tile_type = world.tiles[row][column]
                tile_name = "FLOOR" if tile_type == world.FLOOR else "WALL"
                print(f"  Tile ({column}, {row}): {tile_name}")
            else:
                print(f"  Tile ({column}, {row}): OUT OF BOUNDS")

    # Check collision at spawn
    collides = world.collides_with_wall(player_rect)
    print(f"\nCollision at spawn: {collides}")

    # Check if player is centered on a tile
    tile_center_x = (tile_x * world.TILE_SIZE) + world.TILE_SIZE // 2
    tile_center_y = (tile_y * world.TILE_SIZE) + world.TILE_SIZE // 2

    print(f"\nTile center: ({tile_center_x}, {tile_center_y})")
    print(f"Player center: ({player.rect.centerx}, {player.rect.centery})")
    print(f"Player centered on tile: {player.rect.centerx == tile_center_x and player.rect.centery == tile_center_y}")

    # Check nearby tiles for walls
    print(f"\n=== Nearby Tiles (3x3 area) ===")
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            check_x = tile_x + dx
            check_y = tile_y + dy
            if 0 <= check_x < world.columns and 0 <= check_y < world.rows:
                tile_type = world.tiles[check_y][check_x]
                tile_name = "FLOOR" if tile_type == world.FLOOR else "WALL"
                marker = "*" if dx == 0 and dy == 0 else " "
                print(f"  {marker} Tile ({check_x}, {check_y}): {tile_name}")

    print("\n=== Testing Game Class Spawn ===")
    game = Game()
    print(f"Game player spawn: ({game.player.x}, {game.player.y})")
    print(f"Game player rect: {game.player.rect}")
    print(f"Game player collision: {world.collides_with_wall(game.player.rect)}")

    pygame.quit()


if __name__ == "__main__":
    main()
