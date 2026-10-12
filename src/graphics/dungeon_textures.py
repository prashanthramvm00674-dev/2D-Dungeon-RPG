
import random

import pygame


class DungeonTextures:
    """
    Dark-fantasy dungeon floor materials.

    Features:
    - Irregular, asymmetrical blue-gray stone slabs.
    - Narrow, recessed mortar seams.
    - Layered bevels, chips, pits, mineral grain, and branching cracks.
    - Selective small moss details.
    - Larger transparent moss growths spanning multiple tiles.
    - Deterministic texture generation and caching.

    Does not modify world generation, collision, or gameplay.
    """

    TILE_SIZE = 40

    MORTAR = (17, 26, 34)
    MORTAR_HIGHLIGHT = (28, 40, 49)

    STONE_BASE = (43, 58, 71)
    STONE_DARK = (30, 42, 53)
    STONE_MID = (48, 64, 77)
    STONE_LIGHT = (65, 81, 93)
    STONE_HIGHLIGHT = (88, 104, 113)
    STONE_PALE = (105, 117, 122)

    MOSS_DARK = (30, 48, 30, 220)
    MOSS_GREEN = (45, 70, 35, 230)
    MOSS_MID = (61, 88, 40, 225)
    MOSS_LIGHT = (83, 106, 46, 215)
    MOSS_HIGHLIGHT = (108, 124, 55, 190)

    def __init__(self, seed=731):
        self.seed = int(seed)
        self.floor_tiles = {}
        self.wall_tiles = {}
        self.moss_patch_cache = {}

    @staticmethod
    def _shift_color(color, amount):
        return tuple(
            max(0, min(255, channel + amount))
            for channel in color
        )

    @staticmethod
    def _clamp(value, low, high):
        return max(low, min(high, value))

    def get_floor_tile(self, variant=0):
        """Return a cached 40x40 stone texture."""
        variant = int(variant)

        if variant not in self.floor_tiles:
            self.floor_tiles[variant] = self._create_floor_tile(variant)

        return self.floor_tiles[variant]

    def get_wall_tile(self, variant=0):
        """Return a cached 40x40 wall texture."""
        variant = int(variant)

        if variant not in self.wall_tiles:
            self.wall_tiles[variant] = self._create_wall_tile(variant)

        return self.wall_tiles[variant]

    def _create_floor_tile(self, variant):
        """Create an asymmetrical, detailed stone slab."""
        rng = random.Random(self.seed + variant * 9973)
        size = self.TILE_SIZE

        tile = pygame.Surface((size, size))
        tile.fill(self.MORTAR)

        # A few thin mortar highlights help separate adjacent stones.
        if rng.random() < 0.45:
            pygame.draw.line(
                tile,
                self.MORTAR_HIGHLIGHT,
                (1, 0),
                (rng.randint(5, 15), 0),
            )

        # Keep the stones closely fitted. Large gaps made the previous
        # preview resemble separate pebbles instead of a paved dungeon.
        left = rng.randint(0, 2)
        top = rng.randint(0, 2)
        right = size - rng.randint(1, 3)
        bottom = size - rng.randint(1, 3)

        # Independently vary the corners and edges of each slab.
        tl = rng.randint(3, 7)
        tr = rng.randint(3, 8)
        br = rng.randint(3, 7)
        bl = rng.randint(3, 8)

        p = [
            (left + tl, top + rng.randint(0, 2)),
            (left + rng.randint(10, 15), top),
            (left + rng.randint(20, 27), top + rng.randint(0, 2)),
            (right - tr, top + rng.randint(0, 2)),
            (right, top + rng.randint(3, 7)),
            (right - rng.randint(0, 2), top + rng.randint(12, 18)),
            (right, bottom - br),
            (right - rng.randint(4, 9), bottom),
            (left + rng.randint(20, 27), bottom - rng.randint(0, 2)),
            (left + rng.randint(10, 17), bottom),
            (left + bl, bottom - rng.randint(0, 2)),
            (left, bottom - rng.randint(5, 9)),
            (left + rng.randint(0, 2), top + rng.randint(13, 20)),
        ]

        # Dark underside creates depth at the edge of the slab.
        shadow_points = [
            (
                self._clamp(x + 1, 0, size - 1),
                self._clamp(y + 1, 0, size - 1),
            )
            for x, y in p
        ]
        pygame.draw.polygon(tile, self.STONE_DARK, shadow_points)

        # Subtle color differences prevent every rock from being identical.
        base = self._shift_color(
            self.STONE_BASE,
            rng.randint(-5, 5),
        )
        pygame.draw.polygon(tile, base, p)

        inner_left = left + 3
        inner_right = right - 3
        inner_top = top + 3
        inner_bottom = bottom - 3

        # Broad mineral facets are irregular rather than rectangular noise.
        for _ in range(rng.randint(3, 6)):
            x = rng.randint(inner_left, inner_right - 5)
            y = rng.randint(inner_top, inner_bottom - 4)
            w = rng.randint(4, min(10, inner_right - x))
            h = rng.randint(2, min(7, inner_bottom - y))

            facet = [
                (x, y + rng.randint(0, 2)),
                (x + w - 2, y),
                (x + w, y + rng.randint(1, 3)),
                (x + w - 1, y + h - 1),
                (x + rng.randint(0, 2), y + h),
            ]

            color = rng.choice(
                (
                    self.STONE_DARK,
                    self.STONE_MID,
                    self.STONE_LIGHT,
                )
            )
            pygame.draw.polygon(tile, color, facet)

        # Directional bevels: light from the upper-left, shade below.
        # Draw only portions of edges to avoid a uniform outlined look.
        for i, start in enumerate(p):
            end = p[(i + 1) % len(p)]
            x1, y1 = start
            x2, y2 = end

            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2

            if mid_y < size * 0.33 and rng.random() < 0.82:
                pygame.draw.line(
                    tile,
                    self.STONE_HIGHLIGHT,
                    start,
                    end,
                )
            elif mid_x < size * 0.22 and rng.random() < 0.60:
                pygame.draw.line(
                    tile,
                    self.STONE_LIGHT,
                    start,
                    end,
                )
            elif (
                mid_y > size * 0.68 or mid_x > size * 0.76
            ) and rng.random() < 0.80:
                pygame.draw.line(
                    tile,
                    self.STONE_DARK,
                    start,
                    end,
                )

        # Dense but clustered rock grain. Individual flecks are mostly
        # one pixel wide, preserving detail at normal gameplay scale.
        for _ in range(rng.randint(9, 15)):
            cx = rng.randint(inner_left, inner_right)
            cy = rng.randint(inner_top, inner_bottom)

            cluster_color = rng.choice(
                (
                    self.STONE_DARK,
                    self.STONE_MID,
                    self.STONE_LIGHT,
                )
            )

            for _ in range(rng.randint(3, 8)):
                x = cx + rng.randint(-3, 3)
                y = cy + rng.randint(-2, 2)

                if (
                    inner_left <= x <= inner_right
                    and inner_top <= y <= inner_bottom
                ):
                    tile.set_at((x, y), cluster_color)

        # Tiny pits and occasional pale mineral flecks.
        for _ in range(rng.randint(18, 32)):
            x = rng.randint(inner_left, inner_right)
            y = rng.randint(inner_top, inner_bottom)

            color = rng.choices(
                (
                    self.STONE_DARK,
                    self.STONE_MID,
                    self.STONE_LIGHT,
                    self.STONE_PALE,
                ),
                weights=(35, 35, 25, 5),
                k=1,
            )[0]

            tile.set_at((x, y), color)

        # One or two fractures with uneven branches.
        if rng.random() < 0.84:
            cx = rng.randint(left + 6, right - 6)
            cy = rng.randint(top + 6, bottom - 7)
            dx = rng.choice((-1, 1))

            crack = [
                (cx, cy),
                (cx + dx, cy + 2),
                (cx - dx, cy + 4),
                (cx + dx * 2, cy + 6),
                (cx + dx, cy + 8),
            ]

            pygame.draw.lines(
                tile,
                self.STONE_DARK,
                False,
                crack,
            )

            # Slightly brighter chips beside the fracture.
            for hx, hy in crack[1::2]:
                if 1 <= hx + 1 < size - 1 and 1 <= hy < size - 1:
                    if rng.random() < 0.65:
                        tile.set_at(
                            (hx + 1, hy),
                            self.STONE_LIGHT,
                        )

            if rng.random() < 0.50:
                bx, by = crack[2]
                branch = [
                    (bx, by),
                    (bx + dx * 2, by - 1),
                    (bx + dx * 4, by - 3),
                ]
                pygame.draw.lines(
                    tile,
                    self.STONE_DARK,
                    False,
                    branch,
                )

        # Occasional tiny edge chips.
        for _ in range(rng.randint(0, 3)):
            edge = rng.choice(("left", "right", "top", "bottom"))

            if edge in ("left", "right"):
                x = left if edge == "left" else right
                y = rng.randint(top + 5, bottom - 5)
                tile.set_at((x, y), self.MORTAR)
                if y + 1 < size:
                    tile.set_at((x, y + 1), self.MORTAR)
            else:
                x = rng.randint(left + 5, right - 5)
                y = top if edge == "top" else bottom
                tile.set_at((x, y), self.MORTAR)
                if x + 1 < size:
                    tile.set_at((x + 1, y), self.MORTAR)

        # Small local moss accents. Larger moss growth is drawn separately.
        if rng.random() < 0.20:
            moss_color = rng.choice(
                (
                    (36, 54, 36),
                    (45, 65, 39),
                    (54, 73, 40),
                )
            )
            mx = rng.randint(left + 3, right - 3)
            my = rng.choice(
                (
                    rng.randint(top + 2, top + 7),
                    rng.randint(bottom - 7, bottom - 2),
                )
            )

            for _ in range(rng.randint(4, 9)):
                x = mx + rng.randint(-3, 3)
                y = my + rng.randint(-2, 2)

                if left <= x <= right and top <= y <= bottom:
                    tile.set_at((x, y), moss_color)

        return tile

    def _create_wall_tile(self, variant):
        """Create a textured stone wall with stacked blocks."""
        rng = random.Random(self.seed + variant * 8831)
        size = self.TILE_SIZE

        wall = pygame.Surface((size, size))
        wall.fill(self.MORTAR)

        # Darker wall base color
        wall_base = self._shift_color(self.STONE_BASE, -10)

        # Generate 2-3 stacked stone blocks
        num_blocks = rng.randint(2, 3)
        block_height = size // num_blocks

        for i in range(num_blocks):
            y = i * block_height
            h = block_height if i < num_blocks - 1 else size - y

            # Random horizontal offset for brick pattern
            offset = rng.randint(0, 4) if i % 2 == 0 else rng.randint(-4, 0)

            left = max(0, offset)
            right = min(size, size + offset)
            width = right - left

            if width < 8:
                continue

            # Block base color with slight variation
            block_color = self._shift_color(
                wall_base,
                rng.randint(-8, 8)
            )

            pygame.draw.rect(wall, block_color, (left, y, width, h))

            # Inner detail on block
            inner_left = left + 2
            inner_right = right - 2
            inner_top = y + 2
            inner_bottom = y + h - 2

            if inner_right > inner_left and inner_bottom > inner_top:
                # Add stone grain to block
                for _ in range(rng.randint(3, 6)):
                    gx = rng.randint(inner_left, inner_right)
                    gy = rng.randint(inner_top, inner_bottom)

                    grain_color = rng.choice(
                        (self.STONE_DARK, self.STONE_MID, self.STONE_LIGHT)
                    )

                    for _ in range(rng.randint(2, 4)):
                        px = gx + rng.randint(-2, 2)
                        py = gy + rng.randint(-1, 1)

                        if inner_left <= px <= inner_right and inner_top <= py <= inner_bottom:
                            wall.set_at((px, py), grain_color)

                # Small cracks on block
                if rng.random() < 0.35:
                    cx = rng.randint(inner_left + 3, inner_right - 3)
                    cy = rng.randint(inner_top + 2, inner_bottom - 2)
                    length = rng.randint(3, 8)
                    dx = rng.choice((-1, 1))

                    crack = [(cx + dx * i, cy) for i in range(length)]
                    pygame.draw.lines(wall, self.STONE_DARK, False, crack)

        # Add edge highlights for depth
        pygame.draw.line(wall, self.STONE_LIGHT, (0, 0), (size - 1, 0), 1)
        pygame.draw.line(wall, self.STONE_LIGHT, (0, 0), (0, size - 1), 1)
        pygame.draw.line(wall, self.STONE_DARK, (size - 1, 0), (size - 1, size - 1), 1)
        pygame.draw.line(wall, self.STONE_DARK, (0, size - 1), (size - 1, size - 1), 1)

        # Occasional moss on walls
        if rng.random() < 0.15:
            mx = rng.randint(2, size - 3)
            my = rng.randint(2, size - 3)

            moss_color = rng.choice(
                ((30, 45, 30), (38, 55, 35), (45, 65, 40))
            )

            for _ in range(rng.randint(3, 6)):
                px = mx + rng.randint(-2, 2)
                py = my + rng.randint(-2, 2)

                if 0 <= px < size and 0 <= py < size:
                    wall.set_at((px, py), moss_color)

        return wall

    def get_moss_patch(self, width_tiles=4, height_tiles=2, seed=0):
        """
        Return a cached transparent moss patch spanning several tiles.

        Use this as a visual overlay; it does not affect collisions.
        """
        width_tiles = max(1, int(width_tiles))
        height_tiles = max(1, int(height_tiles))
        seed = int(seed)

        key = (width_tiles, height_tiles, seed)

        if key not in self.moss_patch_cache:
            self.moss_patch_cache[key] = self._create_moss_patch(
                width_tiles,
                height_tiles,
                seed,
            )

        return self.moss_patch_cache[key]

    def _create_moss_patch(self, width_tiles, height_tiles, seed):
        """Generate organic branching moss for a multi-tile overlay."""
        rng = random.Random(self.seed + seed * 7919)

        width = width_tiles * self.TILE_SIZE
        height = height_tiles * self.TILE_SIZE

        moss = pygame.Surface(
            (width, height),
            pygame.SRCALPHA,
        )

        colors = (
            self.MOSS_DARK,
            self.MOSS_GREEN,
            self.MOSS_MID,
            self.MOSS_LIGHT,
            self.MOSS_HIGHLIGHT,
        )

        def point(x, y):
            return (
                self._clamp(int(x), 1, width - 2),
                self._clamp(int(y), 1, height - 2),
            )

        def draw_vein(path, thickness):
            if len(path) < 2:
                return

            pygame.draw.lines(
                moss,
                self.MOSS_DARK,
                False,
                path,
                thickness + 2,
            )
            pygame.draw.lines(
                moss,
                self.MOSS_GREEN,
                False,
                path,
                thickness,
            )

            # Broken brighter segments mimic leafy upper surfaces.
            for x, y in path[1::2]:
                if rng.random() < 0.65:
                    pygame.draw.line(
                        moss,
                        self.MOSS_MID,
                        (x, y),
                        point(x + rng.randint(-2, 2), y - 1),
                    )

        def draw_leaves(path, density=0.8):
            for x, y in path:
                if rng.random() > density:
                    continue

                for _ in range(rng.randint(2, 6)):
                    px = x + rng.randint(-4, 4)
                    py = y + rng.randint(-3, 3)

                    color = rng.choices(
                        colors,
                        weights=(10, 28, 31, 24, 7),
                        k=1,
                    )[0]

                    pygame.draw.rect(
                        moss,
                        color,
                        (
                            px,
                            py,
                            rng.choice((1, 2, 2, 3)),
                            rng.choice((1, 2, 3)),
                        ),
                    )

        def make_path(start, end, segments):
            path = [point(*start)]

            for i in range(1, segments):
                t = i / segments

                x = start[0] + (end[0] - start[0]) * t
                y = start[1] + (end[1] - start[1]) * t

                x += rng.randint(-5, 5)
                y += rng.randint(-4, 4)

                path.append(point(x, y))

            path.append(point(*end))
            return path

        edges = ("top", "right", "bottom", "left")
        routes = []

        # Uneven main branches that sometimes enter or leave at patch edges.
        for _ in range(rng.randint(2, 4)):
            start_edge = rng.choice(edges)
            end_edge = rng.choice(
                [edge for edge in edges if edge != start_edge]
            )

            def edge_point(edge):
                if edge == "top":
                    return (rng.randint(0, width - 1), 0)
                if edge == "bottom":
                    return (rng.randint(0, width - 1), height - 1)
                if edge == "left":
                    return (0, rng.randint(0, height - 1))
                return (width - 1, rng.randint(0, height - 1))

            start = edge_point(start_edge)
            end = edge_point(end_edge)

            path = make_path(
                start,
                end,
                rng.randint(5, 9),
            )
            routes.append(path)

            draw_vein(path, rng.choice((1, 2, 2)))
            draw_leaves(path, density=0.85)

            # Fine side roots split off from the main tendrils.
            for _ in range(rng.randint(2, 4)):
                origin = rng.choice(path[1:-1])
                target = point(
                    origin[0] + rng.randint(-18, 18),
                    origin[1] + rng.randint(-14, 14),
                )
                branch = make_path(
                    origin,
                    target,
                    rng.randint(2, 4),
                )

                draw_vein(branch, 1)
                draw_leaves(branch, density=0.72)

        # Irregular leafy clumps around selected branch intersections.
        for path in routes:
            for x, y in path[1:-1:2]:
                if rng.random() > 0.6:
                    continue

                for _ in range(rng.randint(8, 17)):
                    px = int(x + rng.gauss(0, 4))
                    py = int(y + rng.gauss(0, 3))

                    if not (1 <= px < width - 1 and 1 <= py < height - 1):
                        continue

                    color = rng.choices(
                        colors,
                        weights=(8, 27, 32, 26, 7),
                        k=1,
                    )[0]

                    pygame.draw.rect(
                        moss,
                        color,
                        (
                            px,
                            py,
                            rng.choice((1, 2, 3)),
                            rng.choice((1, 2, 3)),
                        ),
                    )

        return moss
