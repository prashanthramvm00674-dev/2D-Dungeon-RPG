import sys
from pathlib import Path

import pygame

# Add the project's src directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from world.world import World


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))

    # Test World instantiation with textures
    world = World()

    # Verify DungeonTextures is initialized
    assert hasattr(world, 'dungeon_textures'), "World should have dungeon_textures"
    assert world.dungeon_textures is not None, "dungeon_textures should not be None"

    # Verify moss patches are generated
    assert hasattr(world, 'moss_patches'), "World should have moss_patches"
    assert len(world.moss_patches) > 0, "Should have at least one moss patch"

    # Verify moss patches have required fields
    for patch in world.moss_patches:
        assert 'column' in patch, "Moss patch should have column"
        assert 'row' in patch, "Moss patch should have row"
        assert 'width_tiles' in patch, "Moss patch should have width_tiles"
        assert 'height_tiles' in patch, "Moss patch should have height_tiles"
        assert 'seed' in patch, "Moss patch should have seed"

    # Verify moss patches are placed on floor tiles
    for patch in world.moss_patches:
        col, row = patch['column'], patch['row']
        width, height = patch['width_tiles'], patch['height_tiles']

        for r in range(row, row + height):
            for c in range(col, col + width):
                assert world.tiles[r][c] == World.FLOOR, \
                    f"Moss patch at ({col}, {row}) should be on floor tiles"

    # Test determinism: create another world and compare moss patches
    world2 = World()
    assert len(world.moss_patches) == len(world2.moss_patches), \
        "Moss patches should be deterministic"

    for patch1, patch2 in zip(world.moss_patches, world2.moss_patches):
        assert patch1 == patch2, "Moss patch data should be identical"

    # Test texture caching works
    variant = 0
    tile1 = world.dungeon_textures.get_floor_tile(variant)
    tile2 = world.dungeon_textures.get_floor_tile(variant)
    assert tile1 is tile2, "Texture caching should return same surface"

    # Test wall textures
    wall_tile = world.dungeon_textures.get_wall_tile(0)
    assert wall_tile.get_size() == (40, 40), "Wall tile should be 40x40"

    # Test wall texture caching
    wall_tile_2 = world.dungeon_textures.get_wall_tile(0)
    assert wall_tile is wall_tile_2, "Wall texture caching should work"

    pygame.quit()
    print("World texture integration tests passed!")


if __name__ == "__main__":
    main()
