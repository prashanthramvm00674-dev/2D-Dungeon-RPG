import pygame

from graphics.dungeon_textures import DungeonTextures


class World:
    TILE_SIZE = 40

    FLOOR = 0
    WALL = 1
    VOID = 2

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

        # Fixed decorative wall torches also provide lighting source positions.
        self.torches = []
        self._generate_torches()

        # Large-scale flagstones span several 40px gameplay tiles. Keep this
        # entirely visual so movement and collision remain tile-based.
        self.floor_region = self.dungeon_textures.get_floor_region(
            960,
            720,
            seed=1927
        )
        self.floor_region_width, self.floor_region_height = (
            self.floor_region.get_size()
        )
        self.floor_region_variants = {
            (False, False): self.floor_region,
            (True, False): pygame.transform.flip(
                self.floor_region, True, False
            ),
            (False, True): pygame.transform.flip(
                self.floor_region, False, True
            ),
            (True, True): pygame.transform.flip(
                self.floor_region, True, True
            ),
        }

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
        Generate enclosed rooms and connected, two-tile-wide corridors.

        Walkable chambers are FLOOR, their actual masonry boundaries are WALL,
        and the uncarved space between them is VOID. Keeping these three states
        separate prevents the entire map from accidentally becoming walkable.
        """
        import random

        rng = random.Random(12345)

        # Begin with solid dark rock. Room interiors and corridors are carved
        # out explicitly, making the dungeon read as distinct chambers.
        for row in range(self.rows):
            for column in range(self.columns):
                if (
                    row == 0
                    or row == self.rows - 1
                    or column == 0
                    or column == self.columns - 1
                ):
                    self.tiles[row][column] = self.WALL
                else:
                    self.tiles[row][column] = self.VOID

        rooms = []
        target_room_count = 12

        # Place rooms with a two-tile buffer between their bounding boxes.
        # The fixed seed makes the layout deterministic between launches.
        for _ in range(target_room_count):
            room = None

            for _attempt in range(1000):
                room_width = rng.randint(7, 14)
                room_height = rng.randint(6, 11)
                room_x = rng.randint(2, self.columns - room_width - 2)
                room_y = rng.randint(2, self.rows - room_height - 2)

                overlaps = any(
                    not (
                        room_x + room_width + 2 <= placed["x"]
                        or placed["x"] + placed["width"] + 2 <= room_x
                        or room_y + room_height + 2 <= placed["y"]
                        or placed["y"] + placed["height"] + 2 <= room_y
                    )
                    for placed in rooms
                )

                if not overlaps:
                    room = {
                        "x": room_x,
                        "y": room_y,
                        "width": room_width,
                        "height": room_height,
                        "center_x": room_x + room_width // 2,
                        "center_y": room_y + room_height // 2,
                    }
                    break

            # Preserve a valid dungeon if an unusually constrained map cannot
            # fit every requested room.
            if room is None:
                continue

            left = room["x"]
            top = room["y"]
            right = left + room["width"] - 1
            bottom = top + room["height"] - 1

            for row in range(top, bottom + 1):
                for column in range(left, right + 1):
                    is_boundary = (
                        row == top
                        or row == bottom
                        or column == left
                        or column == right
                    )
                    self.tiles[row][column] = (
                        self.WALL if is_boundary else self.FLOOR
                    )

            rooms.append(room)

        def carve_horizontal(start_x, end_x, row):
            """Carve an 80-pixel-wide horizontal leg and its door openings."""
            for column in range(min(start_x, end_x), max(start_x, end_x) + 1):
                for corridor_row in (row, row + 1):
                    if (
                        0 < column < self.columns - 1
                        and 0 < corridor_row < self.rows - 1
                    ):
                        self.tiles[corridor_row][column] = self.FLOOR

        def carve_vertical(column, start_y, end_y):
            """Carve an 80-pixel-wide vertical leg and its door openings."""
            for row in range(min(start_y, end_y), max(start_y, end_y) + 1):
                for corridor_column in (column, column + 1):
                    if (
                        0 < corridor_column < self.columns - 1
                        and 0 < row < self.rows - 1
                    ):
                        self.tiles[row][corridor_column] = self.FLOOR

        def connect_rooms(first, second):
            # Horizontal then vertical creates a continuous L-shaped route.
            carve_horizontal(
                first["center_x"],
                second["center_x"],
                first["center_y"],
            )
            carve_vertical(
                second["center_x"],
                first["center_y"],
                second["center_y"],
            )

        # A spanning chain guarantees every generated room has a route to the
        # rest of the dungeon, even if extra connections are skipped.
        for index in range(len(rooms) - 1):
            connect_rooms(rooms[index], rooms[index + 1])

        # Add deterministic alternate routes so exploration is less linear.
        extra_links = set()
        for _ in range(4):
            if len(rooms) < 2:
                break

            first_index = rng.randrange(len(rooms))
            second_index = rng.randrange(len(rooms) - 1)
            if second_index >= first_index:
                second_index += 1

            pair = tuple(sorted((first_index, second_index)))
            if pair in extra_links:
                continue

            extra_links.add(pair)
            connect_rooms(rooms[first_index], rooms[second_index])

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

    def _generate_torches(self, count=12):
        """
        Place a deterministic set of torches on interior wall tiles.

        Torches are decorative only: they do not alter the tile map, player
        movement, enemy movement, or collision geometry.
        """
        import random

        rng = random.Random(6419)
        candidates = []

        for row in range(2, self.rows - 2):
            for column in range(2, self.columns - 2):
                if self.tiles[row][column] != self.WALL:
                    continue

                adjacent_floor = (
                    not self.is_wall(column, row - 1)
                    or not self.is_wall(column + 1, row)
                    or not self.is_wall(column, row + 1)
                    or not self.is_wall(column - 1, row)
                )

                if adjacent_floor:
                    candidates.append((column, row))

        rng.shuffle(candidates)
        selected = []

        # Relax the spacing gradually if an irregular generated map has fewer
        # widely separated wall locations than requested.
        for min_separation in (8, 6, 4, 2, 0):
            selected = []

            for candidate in candidates:
                if all(
                    (candidate[0] - placed[0]) ** 2
                    + (candidate[1] - placed[1]) ** 2
                    >= min_separation ** 2
                    for placed in selected
                ):
                    selected.append(candidate)

                    if len(selected) >= count:
                        break

            if len(selected) >= min(count, 8):
                break

        self.torches = [
            {
                "tile_x": column,
                "tile_y": row,
                "x": column * self.TILE_SIZE + self.TILE_SIZE // 2,
                "y": row * self.TILE_SIZE + self.TILE_SIZE // 2,
            }
            for column, row in selected
        ]

    def render_torches(self, screen, camera):
        """Draw small pixel-style wall torches over their wall tiles."""
        viewport = screen.get_rect()

        for index, torch in enumerate(self.torches):
            world_rect = pygame.Rect(
                torch["x"] - 9,
                torch["y"] - 14,
                18,
                28
            )
            rect = camera.apply(world_rect)

            if not rect.colliderect(viewport):
                continue

            center_x = rect.centerx
            top_y = rect.top

            # Wall bracket and dark silhouette.
            pygame.draw.rect(
                screen,
                (15, 18, 23),
                pygame.Rect(center_x - 5, top_y + 12, 10, 13)
            )
            pygame.draw.rect(
                screen,
                (105, 67, 41),
                pygame.Rect(center_x - 3, top_y + 10, 6, 14)
            )
            pygame.draw.rect(
                screen,
                (174, 112, 57),
                pygame.Rect(center_x - 4, top_y + 10, 8, 3)
            )

            # A crisp three-layer flame; the small variation is deterministic.
            flame_peak_y = top_y + (index % 3)
            pygame.draw.polygon(
                screen,
                (164, 47, 19),
                [
                    (center_x, flame_peak_y),
                    (center_x - 7, top_y + 13),
                    (center_x - 4, top_y + 18),
                    (center_x + 5, top_y + 18),
                    (center_x + 7, top_y + 12)
                ]
            )
            pygame.draw.polygon(
                screen,
                (255, 124, 32),
                [
                    (center_x, top_y + 4),
                    (center_x - 4, top_y + 13),
                    (center_x, top_y + 17),
                    (center_x + 4, top_y + 12)
                ]
            )
            pygame.draw.polygon(
                screen,
                (255, 220, 105),
                [
                    (center_x, top_y + 10),
                    (center_x - 2, top_y + 14),
                    (center_x, top_y + 16),
                    (center_x + 2, top_y + 13)
                ]
            )

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

        # Any uncarved tile is solid; only explicitly carved floor is walkable.
        return self.tiles[row][column] != self.FLOOR

    def find_path(self, start_tile, goal_tile):
        """
        Return a shortest four-direction path across carved FLOOR tiles.

        The result contains both start and goal tiles. Walls and uncarved VOID
        cells are never traversable, so enemies can follow the actual corridors
        instead of repeatedly pushing against chamber walls.
        """
        from collections import deque

        start = (int(start_tile[0]), int(start_tile[1]))
        goal = (int(goal_tile[0]), int(goal_tile[1]))

        for column, row in (start, goal):
            if (
                column < 0 or column >= self.columns
                or row < 0 or row >= self.rows
                or self.tiles[row][column] != self.FLOOR
            ):
                return []

        if start == goal:
            return [start]

        frontier = deque([start])
        previous = {start: None}
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))

        while frontier:
            current = frontier.popleft()
            if current == goal:
                break

            for dx, dy in directions:
                neighbour = (current[0] + dx, current[1] + dy)
                column, row = neighbour

                if (
                    neighbour in previous
                    or column < 0 or column >= self.columns
                    or row < 0 or row >= self.rows
                    or self.tiles[row][column] != self.FLOOR
                ):
                    continue

                previous[neighbour] = current
                frontier.append(neighbour)

        if goal not in previous:
            return []

        path = []
        node = goal
        while node is not None:
            path.append(node)
            node = previous[node]

        path.reverse()
        return path

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
        """Draw macro flagstones first, then moss, walls, and decorative torches."""
        viewport = screen.get_rect()
        floor_width = self.floor_region_width
        floor_height = self.floor_region_height

        # ==================================================
        # LARGE-SCALE STONE FLOOR
        # ==================================================

        # The surface uses large slabs to match the supplied visual reference.
        # Mirrored repeats keep neighbouring regions seamless at their edges.
        region_columns = (
            self.get_width() + floor_width - 1
        ) // floor_width
        region_rows = (
            self.get_height() + floor_height - 1
        ) // floor_height

        for region_row in range(region_rows):
            world_y = region_row * floor_height

            for region_column in range(region_columns):
                world_x = region_column * floor_width
                world_region = pygame.Rect(
                    world_x,
                    world_y,
                    floor_width,
                    floor_height
                )
                screen_region = camera.apply(world_region)

                if not screen_region.colliderect(viewport):
                    continue

                texture = self.floor_region_variants[
                    (region_column % 2 == 1, region_row % 2 == 1)
                ]
                screen.blit(texture, screen_region.topleft)

        # Work out the visible tile range once. Reuse it for the void mask and
        # wall pass so larger maps do not process off-screen cells every frame.
        first_column = max(0, camera.x // self.TILE_SIZE)
        last_column = min(
            self.columns,
            (camera.x + screen.get_width()) // self.TILE_SIZE + 2
        )
        first_row = max(0, camera.y // self.TILE_SIZE)
        last_row = min(
            self.rows,
            (camera.y + screen.get_height()) // self.TILE_SIZE + 2
        )

        # Mask uncarved space with near-black rock shadow. The macro flagstone
        # texture remains visible only in rooms and corridors that are FLOOR.
        for row in range(first_row, last_row):
            for column in range(first_column, last_column):
                if self.tiles[row][column] != self.VOID:
                    continue

                world_rect = pygame.Rect(
                    column * self.TILE_SIZE,
                    row * self.TILE_SIZE,
                    self.TILE_SIZE,
                    self.TILE_SIZE
                )
                screen_rect = camera.apply(world_rect)
                shade = (
                    3 + (row * 3 + column) % 3,
                    6 + (row + column * 2) % 4,
                    10 + (row * 5 + column * 3) % 5
                )
                screen.fill(shade, screen_rect)

        # ==================================================
        # EXISTING MOSS PATCH OVERLAYS
        # ==================================================

        # Keep the original deterministic moss patches. They are generated
        # only over floor tiles, so walls are not painted over by these details.
        for patch in self.moss_patches:
            world_x = patch["column"] * self.TILE_SIZE
            world_y = patch["row"] * self.TILE_SIZE
            width = patch["width_tiles"] * self.TILE_SIZE
            height = patch["height_tiles"] * self.TILE_SIZE

            world_rect = pygame.Rect(
                world_x,
                world_y,
                width,
                height
            )
            screen_rect = camera.apply(world_rect)

            if not screen_rect.colliderect(viewport):
                continue

            moss_texture = self.dungeon_textures.get_moss_patch(
                patch["width_tiles"],
                patch["height_tiles"],
                patch["seed"]
            )
            screen.blit(moss_texture, screen_rect)

        # ==================================================
        # WALLS ON TOP OF THE FLOOR
        # ==================================================

        # Preserve 40x40 wall geometry, but only inspect tiles that can
        # appear in this viewport. The old full-map scan visited all 4,000
        # cells every frame, even when most of the dungeon was off-screen.
        for row in range(first_row, last_row):
            for column in range(first_column, last_column):
                if self.tiles[row][column] != self.WALL:
                    continue

                world_rect = pygame.Rect(
                    column * self.TILE_SIZE,
                    row * self.TILE_SIZE,
                    self.TILE_SIZE,
                    self.TILE_SIZE
                )
                screen_rect = camera.apply(world_rect)

                if not screen_rect.colliderect(viewport):
                    continue

                variant = (row * self.columns + column) % 12
                wall_texture = self.dungeon_textures.get_wall_tile(variant)
                screen.blit(wall_texture, screen_rect)

        # ==================================================
        # WALL TORCHES
        # ==================================================

        self.render_torches(screen, camera)
