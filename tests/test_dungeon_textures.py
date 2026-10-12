
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

    tile = textures.get_floor_tile(0)
    assert tile.get_size() == (40, 40)

    # Repeated requests should return the cached tile.
    assert textures.get_floor_tile(0) is tile

    # Different variants should have separate cached surfaces.
    other_tile = textures.get_floor_tile(1)
    assert other_tile.get_size() == (40, 40)
    assert other_tile is not tile

    pygame.quit()
    print("Dungeon texture tests passed!")


if __name__ == "__main__":
    main()
