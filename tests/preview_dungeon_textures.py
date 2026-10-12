
import sys
from pathlib import Path

import pygame

# Make the project's src folder importable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from graphics.dungeon_textures import DungeonTextures


def main():
    pygame.init()

    tile_size = DungeonTextures.TILE_SIZE
    columns = 8
    rows = 5
    scale = 4

    screen = pygame.display.set_mode(
        (columns * tile_size * scale, rows * tile_size * scale)
    )
    pygame.display.set_caption("Dungeon Stone Texture Preview")

    textures = DungeonTextures()
    clock = pygame.time.Clock()

    tiles = [
        textures.get_floor_tile(index)
        for index in range(columns * rows)
    ]

    # Scale each tile once, not every frame.
    preview_tiles = [
        pygame.transform.scale(
            tile,
            (tile_size * scale, tile_size * scale),
        )
        for tile in tiles
    ]

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((18, 20, 25))

        for index, tile in enumerate(preview_tiles):
            x = (index % columns) * tile_size * scale
            y = (index // columns) * tile_size * scale
            screen.blit(tile, (x, y))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
