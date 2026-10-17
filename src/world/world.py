import pygame

from graphics.dungeon_textures import DungeonTextures


class World:
    TILE_SIZE = 40

    FLOOR = 0
    WALL = 1

    def __init__(self):
        self.columns = 80
        self.rows = 50

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

    def _is_safe_spawn_tile(self, column, row, clearance=1):
        """Return True when a floor tile has enough clear space around it."""
        if not (0 < column < self.columns - 1):
            return False
        if not (0 < row < self.rows - 1):
            return False
        if self.tiles[row][column] != self.FLOOR:
            return False

        for offset_y in range(-clearance, clearance + 1):
            for offset_x in range(-clearance, clearance + 1):
                if self.is_wall(column + offset_x, row + offset_y):
                    return False

        return True

    def _get_safe_spawn_tiles(self):
        """Collect floor tiles with a one-tile wall clearance."""
        return [
            (column, row)
            for row in range(1, self.rows - 1)
            for column in range(1, self.columns - 1)
            if self._is_safe_spawn_tile(column, row)
        ]

    def get_center_spawn_position(self):
        """
        Return a safe tile nearest the dungeon's center.

        Coordinates are in world pixels and match Player.rect and Enemy.rect.
        """
        safe_tiles = self._get_safe_spawn_tiles()
        if not safe_tiles:
            # Defensive fallback for an unexpectedly closed dungeon.
            return (
                max(0, (self.get_width() - 40) // 2),
                max(0, (self.get_height() - 40) // 2)
            )

        center_column = (self.columns - 1) / 2
        center_row = (self.rows - 1) / 2
        column, row = min(
            safe_tiles,
            key=lambda tile: (
                (tile[0] - center_column) ** 2
                + (tile[1] - center_row) ** 2,
                tile[1],
                tile[0]
            )
        )
        return (column * self.TILE_SIZE, row * self.TILE_SIZE)

    def get_safe_spawn_position(self):
        """Backward-compatible alias for the safe central spawn."""
        return self.get_center_spawn_position()

    def get_edge_spawn_positions(self, count, avoid_positions=None):
        """
        Return separated, safe enemy positions near the dungeon's edges.

        avoid_positions accepts world-pixel (x, y) positions to keep clear.
        """
        if count <= 0:
            return []

        safe_tiles = self._get_safe_spawn_tiles()
        if not safe_tiles:
            fallback = self.get_center_spawn_position()
            return [fallback for _ in range(count)]

        if avoid_positions is None:
            avoid_positions = []

        used_tiles = [
            (int(x) // self.TILE_SIZE, int(y) // self.TILE_SIZE)
            for x, y in avoid_positions
        ]

        def edge_depth(tile):
            column, row = tile
            return min(
                column, row,
                self.columns - 1 - column,
                self.rows - 1 - row
            )

        # Spawn inside the boundary wall, preferring the outer ten-tile band.
        edge_candidates = [
            tile for tile in safe_tiles if edge_depth(tile) <= 10
        ]
        if len(edge_candidates) < count:
            edge_candidates = [
                tile for tile in safe_tiles if edge_depth(tile) <= 15
            ]
        if not edge_candidates:
            edge_candidates = safe_tiles[:]

        targets = [
            (5, 5),
            (self.columns - 6, 5),
            (5, self.rows - 6),
            (self.columns - 6, self.rows - 6)
        ]
        selected = []

        for index in range(count):
            target = targets[index % len(targets)]
            target_left = target[0] < self.columns // 2
            target_top = target[1] < self.rows // 2

            quadrant_candidates = [
                tile for tile in edge_candidates
                if (tile[0] < self.columns // 2) == target_left
                and (tile[1] < self.rows // 2) == target_top
            ]
            if not quadrant_candidates:
                quadrant_candidates = edge_candidates

            chosen = None
            for min_separation in (10, 7, 4, 1, 0):
                pool = [
                    tile for tile in quadrant_candidates
                    if tile not in selected
                    and all(
                        (tile[0] - used[0]) ** 2
                        + (tile[1] - used[1]) ** 2
                        >= min_separation ** 2
                        for used in used_tiles
                    )
                ]
                if pool:
                    chosen = min(
                        pool,
                        key=lambda tile: (
                            (tile[0] - target[0]) ** 2
                            + (tile[1] - target[1]) ** 2,
                            edge_depth(tile),
                            tile[1],
                            tile[0]
                        )
                    )
                    break

            if chosen is None:
                remaining = [tile for tile in safe_tiles if tile not in selected]
                if not remaining:
                    break
                chosen = max(
                    remaining,
                    key=lambda tile: (
                        min(
                            ((tile[0] - used[0]) ** 2
                             + (tile[1] - used[1]) ** 2)
                            for used in used_tiles
                        ) if used_tiles else 0,
                        -edge_depth(tile)
                    )
                )

            selected.append(chosen)
            used_tiles.append(chosen)

        return [
            (column * self.TILE_SIZE, row * self.TILE_SIZE)
            for column, row in selected
        ]

    def create_dungeon(self):
        """
        Procedurally generate an 80x50 dungeon with connected rooms and corridors.

        Creates a natural, expansive dungeon layout with:
        - Multiple rooms of varying sizes
        - Corridors connecting rooms
        - Deterministic generation for consistent layouts
        """
        import random

        rng = random.Random(12345)  # Fixed seed for consistency

        # Clear interior
        for row in range(1, self.rows - 1):
            for column in range(1, self.columns - 1):
                self.tiles[row][column] = self.FLOOR

        # Generate rooms
        rooms = []
        num_rooms = 12

        for _ in range(num_rooms):
            # Random room size (6-15 tiles wide, 5-12 tiles tall)
            room_width = rng.randint(6, 15)
            room_height = rng.randint(5, 12)

            # Random position (with padding from edges)
            room_x = rng.randint(2, self.columns - room_width - 2)
            room_y = rng.randint(2, self.rows - room_height - 2)

            # Create room walls
            for row in range(room_y, room_y + room_height):
                self.tiles[row][room_x] = self.WALL
                self.tiles[row][room_x + room_width - 1] = self.WALL

            for column in range(room_x, room_x + room_width):
                self.tiles[room_y][column] = self.WALL
                self.tiles[room_y + room_height - 1][column] = self.WALL

            rooms.append({
                'x': room_x,
                'y': room_y,
                'width': room_width,
                'height': room_height,
                'center_x': room_x + room_width // 2,
                'center_y': room_y + room_height // 2
            })

        # Connect rooms with corridors
        for i in range(len(rooms) - 1):
            room1 = rooms[i]
            room2 = rooms[i + 1]

            # Create horizontal corridor
            start_x = min(room1['center_x'], room2['center_x'])
            end_x = max(room1['center_x'], room2['center_x'])
            corridor_y = room1['center_y']

            for column in range(start_x, end_x + 1):
                # Clear corridor (remove walls)
                if self.tiles[corridor_y][column] == self.WALL:
                    self.tiles[corridor_y][column] = self.FLOOR

            # Create vertical corridor
            start_y = min(room1['center_y'], room2['center_y'])
            end_y = max(room1['center_y'], room2['center_y'])
            corridor_x = room2['center_x']

            for row in range(start_y, end_y + 1):
                if self.tiles[row][corridor_x] == self.WALL:
                    self.tiles[row][corridor_x] = self.FLOOR

        # Add some additional connecting corridors for more paths
        for _ in range(4):
            idx1 = rng.randint(0, len(rooms) - 1)
            idx2 = rng.randint(0, len(rooms) - 1)

            if idx1 == idx2:
                continue

            room1 = rooms[idx1]
            room2 = rooms[idx2]

            # Horizontal then vertical corridor
            start_x = min(room1['center_x'], room2['center_x'])
            end_x = max(room1['center_x'], room2['center_x'])
            corridor_y = room1['center_y']

            for column in range(start_x, end_x + 1):
                if self.tiles[corridor_y][column] == self.WALL:
                    self.tiles[corridor_y][column] = self.FLOOR

            start_y = min(room1['center_y'], room2['center_y'])
            end_y = max(room1['center_y'], room2['center_y'])
            corridor_x = room2['center_x']

            for row in range(start_y, end_y + 1):
                if self.tiles[row][corridor_x] == self.WALL:
                    self.tiles[row][corridor_x] = self.FLOOR

    def _generate_moss_patches(self):
        """
        Generate deterministic moss patch overlays for floor tiles.

        Places moss patches at random floor locations with fixed seeds
        to ensure consistent visuals across frames.
        """
        import random

        rng = random.Random(42)

        # Place moss patches across the expanded dungeon (more patches for larger map)
        for i in range(20):
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