import sys
from pathlib import Path

import pygame

# Add the project's src directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from graphics.dungeon_textures import DungeonTextures


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))

    textures = DungeonTextures()

    # Test wall tile generation
    wall_tile = textures.get_wall_tile(0)
    assert wall_tile.get_size() == (40, 40), "Wall tile should be 40x40"

    # Test caching
    wall_tile_2 = textures.get_wall_tile(0)
    assert wall_tile is wall_tile_2, "Wall tiles should be cached"

    # Test different variants
    wall_tile_3 = textures.get_wall_tile(1)
    assert wall_tile_3.get_size() == (40, 40), "Variant wall tile should be 40x40"
    assert wall_tile_3 is not wall_tile, "Different variants should have different surfaces"

    # Test multiple variants
    for i in range(12):
        tile = textures.get_wall_tile(i)
        assert tile.get_size() == (40, 40), f"Wall tile variant {i} should be 40x40"

    pygame.quit()
    print("Wall texture tests passed!")


if __name__ == "__main__":
    main()
