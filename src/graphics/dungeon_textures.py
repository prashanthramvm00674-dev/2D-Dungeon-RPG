
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
        self.floor_region_cache = {}
        self.wall_tiles = {}
        self.void_tiles = {}
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

    def get_floor_region(self, width=960, height=720, seed=1927):
        """Return a cached large-scale flagstone floor texture region."""
        key = (int(width), int(height), int(seed))
        if key not in self.floor_region_cache:
            self.floor_region_cache[key] = self._create_floor_region(*key)
        return self.floor_region_cache[key]

    def _create_floor_region(self, width, height, seed):
        """
        Generate a large flagstone region inspired by the supplied reference:
        broad blue-gray slabs, deep joints, chipped bevels, cracks, and moss.
        This is visual-only; world tiles remain 40x40 for collision.
        """
        rng = random.Random(self.seed + seed * 3571)
        width = max(160, int(width))
        height = max(160, int(height))

        mortar = (15, 23, 30)
        mortar_highlight = (23, 34, 42)
        stone_palette = (
            (35, 50, 62),
            (39, 54, 67),
            (43, 58, 71),
            (46, 62, 75),
            (49, 64, 76),
            (40, 55, 68),
            (52, 66, 78),
        )
        shade = (24, 36, 46)
        bevel_light = (76, 91, 103)
        bevel_mid = (61, 77, 90)
        fleck_palette = (
            (27, 40, 51),
            (56, 72, 84),
            (68, 82, 93),
            (81, 94, 103),
        )

        surface = pygame.Surface((width, height))
        surface.fill(mortar)

        # Recessed seams sit beneath each slab for depth.
        pygame.draw.line(
            surface, mortar_highlight, (0, 0), (width - 1, 0), 2
        )
        pygame.draw.line(
            surface, (9, 15, 21), (0, height - 1), (width - 1, height - 1), 3
        )

        y = -rng.randint(0, 30)
        row_index = 0
        while y < height + 120:
            row_height = rng.randint(66, 112)
            seam = rng.randint(5, 9)
            x = -rng.randint(25, 85) if row_index % 2 else -rng.randint(0, 45)

            while x < width + 120:
                block_width = rng.randint(76, 158)
                left = x + seam // 2
                top = y + seam // 2
                right = x + block_width - seam // 2
                bottom = y + row_height - seam // 2

                if right <= left + 18 or bottom <= top + 18:
                    x += block_width
                    continue

                # Irregular corners and small chips make the slabs less uniform.
                cut_tl = rng.randint(4, 13)
                cut_tr = rng.randint(4, 15)
                cut_br = rng.randint(4, 14)
                cut_bl = rng.randint(4, 16)
                points = [
                    (left + cut_tl, top + rng.randint(0, 4)),
                    (left + int((right - left) * rng.uniform(0.34, 0.52)), top),
                    (right - cut_tr, top + rng.randint(0, 5)),
                    (right, top + rng.randint(5, 14)),
                    (right - rng.randint(0, 4), bottom - cut_br),
                    (right - rng.randint(10, 25), bottom),
                    (left + rng.randint(16, 35), bottom - rng.randint(0, 3)),
                    (left + cut_bl, bottom),
                    (left, bottom - rng.randint(8, 20)),
                    (left + rng.randint(0, 4), top + rng.randint(14, 28)),
                ]

                # Shadow underneath the slab.
                shadow_points = [
                    (px + 2, py + 3) for px, py in points
                ]
                pygame.draw.polygon(surface, (7, 13, 19), shadow_points)
                pygame.draw.polygon(surface, shade, points)

                base = rng.choice(stone_palette)
                face_points = [
                    (px, py - 2 if py > top else py + 1)
                    for px, py in points
                ]
                pygame.draw.polygon(surface, base, face_points)

                # Subtle uneven mineral planes across each broad face.
                for _ in range(rng.randint(3, 7)):
                    fx = rng.randint(left + 8, max(left + 8, right - 18))
                    fy = rng.randint(top + 8, max(top + 8, bottom - 14))
                    fw = rng.randint(10, min(34, max(10, right - fx)))
                    fh = rng.randint(5, min(20, max(5, bottom - fy)))
                    facet = [
                        (fx, fy + rng.randint(1, 5)),
                        (fx + fw // 2, fy),
                        (fx + fw, fy + rng.randint(1, 6)),
                        (fx + fw - rng.randint(2, 8), fy + fh),
                        (fx + rng.randint(2, 8), fy + fh - rng.randint(0, 3)),
                    ]
                    pygame.draw.polygon(
                        surface,
                        rng.choice(((30, 44, 55), (48, 63, 76), (57, 72, 84))),
                        facet
                    )

                # Broken top and left bevel highlights; darker lower/right edges.
                pygame.draw.lines(
                    surface,
                    bevel_light,
                    False,
                    points[:3],
                    2
                )
                pygame.draw.lines(
                    surface,
                    bevel_mid,
                    False,
                    points[7:10],
                    1
                )
                pygame.draw.lines(
                    surface,
                    (19, 29, 38),
                    False,
                    points[3:7],
                    2
                )

                inner_left = max(0, left + 8)
                inner_right = min(width - 1, right - 8)
                inner_top = max(0, top + 8)
                inner_bottom = min(height - 1, bottom - 8)

                # Grain clusters and small mineral chips.
                for _ in range(rng.randint(45, 95)):
                    px = rng.randint(inner_left, max(inner_left, inner_right))
                    py = rng.randint(inner_top, max(inner_top, inner_bottom))
                    color = rng.choice(fleck_palette)
                    size = rng.choices((1, 2, 3), weights=(5, 4, 1), k=1)[0]
                    pygame.draw.rect(surface, color, (px, py, size, size))

                # Main fissure with a few angular turns and a tiny branch.
                if rng.random() < 0.78 and inner_right - inner_left > 24:
                    cx = rng.randint(inner_left + 8, max(inner_left + 8, inner_right - 8))
                    cy = rng.randint(inner_top + 8, max(inner_top + 8, inner_bottom - 8))
                    direction = rng.choice((-1, 1))
                    length = rng.randint(12, 29)
                    crack = [
                        (cx, cy),
                        (cx + direction * 3, cy + 4),
                        (cx + direction * 1, cy + 8),
                        (cx + direction * 5, cy + 12),
                        (cx + direction * 4, cy + length),
                    ]
                    pygame.draw.lines(surface, (24, 36, 46), False, crack, 2)
                    pygame.draw.lines(surface, (59, 73, 83), False, crack[:3], 1)
                    if rng.random() < 0.45:
                        bx, by = crack[2]
                        pygame.draw.lines(
                            surface,
                            (25, 38, 47),
                            False,
                            [(bx, by), (bx - direction * 5, by + 3), (bx - direction * 9, by + 8)],
                            1
                        )

                x += block_width
            y += row_height
            row_index += 1

        # Moss grows in organic clusters along a few seams instead of evenly
        # tinting every tile. The same deterministic seed keeps it stable.
        moss_clusters = max(5, width * height // 90000)
        moss_colors = (
            (24, 43, 26),
            (34, 55, 30),
            (46, 68, 34),
            (59, 82, 39),
            (76, 96, 45),
        )
        for _ in range(moss_clusters):
            cx = rng.randint(0, width - 1)
            cy = rng.randint(0, height - 1)
            angle = rng.uniform(-0.8, 0.8)
            span = rng.randint(30, 105)
            branch_points = []
            for step in range(7):
                t = step / 6
                px = self._clamp(
                    int(cx + (t - 0.5) * span),
                    0,
                    width - 1
                )
                py = self._clamp(
                    int(cy + (t - 0.5) * span * angle + rng.randint(-5, 5)),
                    0,
                    height - 1
                )
                branch_points.append((px, py))

            pygame.draw.lines(surface, (18, 32, 20), False, branch_points, 5)
            pygame.draw.lines(surface, (35, 54, 28), False, branch_points, 3)

            for px, py in branch_points:
                for _ in range(rng.randint(5, 13)):
                    leaf_x = px + rng.randint(-11, 11)
                    leaf_y = py + rng.randint(-7, 7)
                    leaf_w = rng.choice((1, 2, 3, 4))
                    leaf_h = rng.choice((1, 2, 3))
                    color = rng.choice(moss_colors)
                    pygame.draw.rect(
                        surface,
                        color,
                        (leaf_x, leaf_y, leaf_w, leaf_h)
                    )

        return surface

    def get_void_tile(self, variant=0):
        """Return a cached slate-rubble tile for uncarved areas between rooms."""
        variant = int(variant) % 24
        if variant not in self.void_tiles:
            self.void_tiles[variant] = self._create_void_tile(variant)
        return self.void_tiles[variant]

    def _create_void_tile(self, variant):
        """
        Create subdued grey-blue rubble rather than an empty near-black cell.

        These cells remain solid for collision and pathfinding; this texture is
        purely environmental, suggesting fallen slate and rough cavern floor.
        """
        rng = random.Random(self.seed + 45017 + variant * 2371)
        size = self.TILE_SIZE
        tile = pygame.Surface((size, size))
        tile.fill((25, 33, 39))

        # Deep joints frame the tile without creating a bright, obvious grid.
        pygame.draw.lines(
            tile, (13, 19, 24), False,
            [(0, 0), (size - 1, 0), (size - 1, size - 1)], 2
        )
        pygame.draw.lines(
            tile, (49, 59, 65), False,
            [(1, 1), (size - 3, 1), (size - 3, size - 3)], 1
        )

        # Three to five fractured slate fragments create varied, stony texture.
        palette = (
            (31, 42, 49),
            (36, 47, 54),
            (41, 51, 57),
            (45, 54, 60),
            (34, 44, 51),
            (48, 56, 61),
        )
        for _ in range(rng.randint(3, 5)):
            cx = rng.randint(7, size - 8)
            cy = rng.randint(7, size - 8)
            rx = rng.randint(4, 11)
            ry = rng.randint(3, 8)
            points = [
                (self._clamp(cx - rx, 1, size - 2), self._clamp(cy - ry // 2, 1, size - 2)),
                (self._clamp(cx - rx // 2, 1, size - 2), self._clamp(cy - ry, 1, size - 2)),
                (self._clamp(cx + rx, 1, size - 2), self._clamp(cy - ry // 3, 1, size - 2)),
                (self._clamp(cx + rx // 2, 1, size - 2), self._clamp(cy + ry, 1, size - 2)),
                (self._clamp(cx - rx // 2, 1, size - 2), self._clamp(cy + ry // 2, 1, size - 2)),
            ]
            pygame.draw.polygon(tile, (15, 22, 28), [(x + 1, y + 2) for x, y in points])
            pygame.draw.polygon(tile, rng.choice(palette), points)
            pygame.draw.lines(tile, (61, 71, 76), False, points[:3], 1)
            pygame.draw.lines(tile, (20, 28, 34), False, points[2:], 1)

        # Fine pale chips and dark gravel give the recesses a natural texture.
        for _ in range(rng.randint(18, 32)):
            px = rng.randint(2, size - 3)
            py = rng.randint(2, size - 3)
            color = rng.choice((
                (17, 25, 31),
                (23, 32, 38),
                (53, 62, 67),
                (59, 67, 71),
            ))
            width = rng.choice((1, 1, 2, 3))
            pygame.draw.rect(tile, color, (px, py, width, rng.choice((1, 2))))

        # Occasional short fractures keep some cells from looking too uniform.
        if rng.random() < 0.72:
            cx = rng.randint(8, size - 9)
            cy = rng.randint(8, size - 9)
            direction = rng.choice((-1, 1))
            crack = [
                (cx, cy),
                (cx + direction * 2, cy + 3),
                (cx - direction, cy + 6),
                (cx + direction * 3, cy + 9),
            ]
            pygame.draw.lines(tile, (14, 22, 28), False, crack, 2)
            if rng.random() < 0.5:
                pygame.draw.lines(tile, (65, 73, 76), False, crack[:2], 1)

        # Dusty, lightly lifted upper edge and shaded lower edge.
        pygame.draw.line(tile, (45, 55, 61), (3, 2), (size - 5, 2), 1)
        pygame.draw.line(tile, (17, 24, 29), (2, size - 2), (size - 2, size - 2), 2)
        return tile

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
