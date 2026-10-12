import pygame

from graphics.dungeon_textures import DungeonTextures


class World:
    TILE_SIZE = 40

    FLOOR = 0
    WALL = 1

    def __init__(self):
        self.columns = 40
        self.rows = 25

        self.floor_color = (45, 45, 50)
        self.wall_color = (80, 80, 90)
        self.grid_color = (55, 55, 60)

        self.tiles = []

        for row in range(self.rows):
            tile_row = []

            for column in range(self.columns):
                if (
                    row == 0
                    or row == self.rows - 1
                    or column == 0
                    or column == self.columns - 1
                ):
                    tile_row.append(self.WALL)
                else:
                    tile_row.append(self.FLOOR)

            self.tiles.append(tile_row)

        self.create_dungeon()

        # ==================================================
        # TEXTURES
        # ==================================================

        self.dungeon_textures = DungeonTextures(seed=731)

        # ==================================================
        # MOSS PATCHES
        # ==================================================

        self.moss_patches = []
        self._generate_moss_patches()

    def create_dungeon(self):
        # Clear interior
        for row in range(1, self.rows - 1):
            for column in range(1, self.columns - 1):
                self.tiles[row][column] = self.FLOOR

        # =========================
        # LEFT ROOM
        # =========================

        for column in range(3, 12):
            self.tiles[4][column] = self.WALL

        for column in range(3, 12):
            self.tiles[13][column] = self.WALL

        for row in range(4, 14):
            self.tiles[row][3] = self.WALL

        # 80px doorway
        for row in range(4, 8):
            self.tiles[row][11] = self.WALL

        for row in range(10, 14):
            self.tiles[row][11] = self.WALL

        # =========================
        # RIGHT ROOM
        # =========================

        for column in range(20, 29):
            self.tiles[4][column] = self.WALL

        for column in range(20, 29):
            self.tiles[13][column] = self.WALL

        for row in range(4, 14):
            self.tiles[row][28] = self.WALL

        # 80px doorway
        for row in range(4, 8):
            self.tiles[row][20] = self.WALL

        for row in range(10, 14):
            self.tiles[row][20] = self.WALL

        # =========================
        # CENTRAL CORRIDOR
        # =========================

        for column in range(11, 21):
            self.tiles[7][column] = self.WALL

        for column in range(11, 21):
            self.tiles[10][column] = self.WALL

        # 80px openings
        self.tiles[7][15] = self.FLOOR
        self.tiles[7][16] = self.FLOOR

        self.tiles[10][15] = self.FLOOR
        self.tiles[10][16] = self.FLOOR

        # =========================
        # LOWER ROOM
        # =========================

        for column in range(14, 27):
            self.tiles[18][column] = self.WALL

        for column in range(14, 27):
            self.tiles[23][column] = self.WALL

        for row in range(18, 24):
            self.tiles[row][14] = self.WALL

        for row in range(18, 24):
            self.tiles[row][26] = self.WALL

        # Doorway into lower room
        self.tiles[18][19] = self.FLOOR
        self.tiles[18][20] = self.FLOOR

    def _generate_moss_patches(self):
        """
        Generate deterministic moss patch overlays for floor tiles.

        Places moss patches at random floor locations with fixed seeds
        to ensure consistent visuals across frames.
        """
        import random

        rng = random.Random(42)

        # Place several moss patches across the dungeon
        for i in range(8):
            # Find a random floor tile position
            for _ in range(100):
                row = rng.randint(1, self.rows - 2)
                column = rng.randint(1, self.columns - 2)

                if self.tiles[row][column] == self.FLOOR:
                    # Random patch size (2-4 tiles wide, 1-3 tiles tall)
                    width = rng.randint(2, 4)
                    height = rng.randint(1, 3)

                    # Ensure patch stays within bounds
                    if column + width > self.columns - 1:
                        width = self.columns - 1 - column
                    if row + height > self.rows - 1:
                        height = self.rows - 1 - row

                    if width < 1 or height < 1:
                        continue

                    # Check all tiles in patch are floor
                    valid = True
                    for r in range(row, row + height):
                        for c in range(column, column + width):
                            if self.tiles[r][c] != self.FLOOR:
                                valid = False
                                break
                        if not valid:
                            break

                    if valid:
                        self.moss_patches.append({
                            'column': column,
                            'row': row,
                            'width_tiles': width,
                            'height_tiles': height,
                            'seed': i + 100
                        })
                        break

    def get_width(self):
        return self.columns * self.TILE_SIZE

    def get_height(self):
        return self.rows * self.TILE_SIZE

    def is_wall(self, column, row):
        if (
            column < 0
            or column >= self.columns
            or row < 0
            or row >= self.rows
        ):
            return True

        return self.tiles[row][column] == self.WALL

    def collides_with_wall(self, rect):
        left = rect.left // self.TILE_SIZE
        right = (rect.right - 1) // self.TILE_SIZE
        top = rect.top // self.TILE_SIZE
        bottom = (rect.bottom - 1) // self.TILE_SIZE

        for row in range(top, bottom + 1):
            for column in range(left, right + 1):
                if self.is_wall(column, row):
                    wall_rect = pygame.Rect(
                        column * self.TILE_SIZE,
                        row * self.TILE_SIZE,
                        self.TILE_SIZE,
                        self.TILE_SIZE
                    )

                    if rect.colliderect(wall_rect):
                        return True

        return False

    def render(self, screen, camera):
        for row in range(self.rows):
            for column in range(self.columns):
                tile = self.tiles[row][column]

                world_rect = pygame.Rect(
                    column * self.TILE_SIZE,
                    row * self.TILE_SIZE,
                    self.TILE_SIZE,
                    self.TILE_SIZE
                )

                screen_rect = camera.apply(world_rect)

                # Skip tiles outside screen
                if not screen_rect.colliderect(
                    screen.get_rect()
                ):
                    continue

                if tile == self.WALL:
                    # Wall tiles use textured stone blocks
                    # Deterministic variant based on tile position
                    variant = (row * self.columns + column) % 12
                    wall_texture = self.dungeon_textures.get_wall_tile(variant)

                    screen.blit(wall_texture, screen_rect)
                else:
                    # Floor tiles use detailed stone textures
                    # Deterministic variant based on tile position
                    variant = (row * self.columns + column) % 16
                    floor_texture = self.dungeon_textures.get_floor_tile(variant)

                    screen.blit(floor_texture, screen_rect)

        # ==================================================
        # MOSS PATCH OVERLAYS
        # ==================================================

        for patch in self.moss_patches:
            world_x = patch['column'] * self.TILE_SIZE
            world_y = patch['row'] * self.TILE_SIZE
            width = patch['width_tiles'] * self.TILE_SIZE
            height = patch['height_tiles'] * self.TILE_SIZE

            world_rect = pygame.Rect(world_x, world_y, width, height)
            screen_rect = camera.apply(world_rect)

            # Skip patches outside screen
            if not screen_rect.colliderect(screen.get_rect()):
                continue

            moss_texture = self.dungeon_textures.get_moss_patch(
                patch['width_tiles'],
                patch['height_tiles'],
                patch['seed']
            )

            screen.blit(moss_texture, screen_rect)