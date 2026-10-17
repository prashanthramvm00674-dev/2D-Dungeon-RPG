import pygame


class HUD:
    """Dark-fantasy pixel-styled HUD matching the target composition."""

    GOLD = (235, 159, 65)
    GOLD_LIGHT = (255, 204, 112)
    GOLD_DARK = (102, 62, 35)
    PANEL = (8, 14, 21)
    PANEL_INNER = (15, 20, 26)
    TEXT = (232, 226, 210)
    MUTED = (143, 151, 158)
    HEART_RED = (224, 45, 48)
    HEART_DARK = (65, 27, 31)

    def __init__(self):
        self._font_cache = {}
        self.menu_button_rect = pygame.Rect(0, 0, 0, 0)

    def _font(self, size, bold=False):
        key = (int(size), bool(bold))
        if key not in self._font_cache:
            self._font_cache[key] = pygame.font.SysFont(
                "serif",
                max(10, int(size)),
                bold=bold
            )
        return self._font_cache[key]

    def _frame(self, screen, rect, fill=None):
        """Layer shadow, dark metal, and broken gold edge highlights."""
        shadow = rect.move(3, 4)
        pygame.draw.rect(screen, (2, 4, 7), shadow)
        pygame.draw.rect(screen, self.GOLD_DARK, rect)
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(screen, self.PANEL if fill is None else fill, inner)

        if inner.width > 8 and inner.height > 8:
            pygame.draw.rect(
                screen,
                (183, 113, 52),
                inner.inflate(-3, -3),
                1
            )

        # Broken edge highlights and clipped corners read like worn brass.
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        hi = self.GOLD_LIGHT
        mid = self.GOLD
        pygame.draw.lines(
            screen, hi, False,
            [(x + 6, y + 2), (x + w - 7, y + 2), (x + w - 3, y + 6)],
            2
        )
        pygame.draw.lines(
            screen, mid, False,
            [(x + 2, y + 7), (x + 2, y + h - 7), (x + 7, y + h - 3),
             (x + w - 7, y + h - 3)],
            2
        )
        pygame.draw.lines(
            screen, self.GOLD_DARK, False,
            [(x + w - 3, y + 7), (x + w - 3, y + h - 7),
             (x + w - 8, y + h - 3)],
            2
        )

    def _draw_skull_badge(self, screen, rect):
        self._frame(screen, rect)
        cx = rect.centerx
        top = rect.y + rect.height // 5
        width = rect.width * 0.48
        height = rect.height * 0.56
        skull = [
            (int(cx - width * 0.62), int(top + height * 0.18)),
            (int(cx - width * 0.46), int(top - height * 0.06)),
            (int(cx), int(top - height * 0.16)),
            (int(cx + width * 0.46), int(top - height * 0.06)),
            (int(cx + width * 0.62), int(top + height * 0.18)),
            (int(cx + width * 0.48), int(top + height * 0.63)),
            (int(cx + width * 0.25), int(top + height * 0.78)),
            (int(cx - width * 0.25), int(top + height * 0.78)),
            (int(cx - width * 0.48), int(top + height * 0.63)),
        ]
        pygame.draw.polygon(screen, (224, 158, 65), skull)
        pygame.draw.polygon(screen, (255, 208, 113), skull, 2)

        eye_y = int(top + height * 0.34)
        eye_rx = max(3, int(width * 0.19))
        eye_ry = max(3, int(height * 0.11))
        pygame.draw.ellipse(
            screen, (15, 17, 20),
            (int(cx - width * 0.42), eye_y, eye_rx * 2, eye_ry * 2)
        )
        pygame.draw.ellipse(
            screen, (15, 17, 20),
            (int(cx + width * 0.05), eye_y, eye_rx * 2, eye_ry * 2)
        )
        nose = [
            (cx, int(top + height * 0.43)),
            (int(cx - width * 0.12), int(top + height * 0.59)),
            (int(cx + width * 0.12), int(top + height * 0.59)),
        ]
        pygame.draw.polygon(screen, (24, 24, 23), nose)
        tooth_y = int(top + height * 0.72)
        pygame.draw.line(
            screen, (73, 48, 30),
            (int(cx - width * 0.28), tooth_y),
            (int(cx + width * 0.28), tooth_y), 2
        )
        for tooth in (-0.15, 0, 0.15):
            tx = int(cx + width * tooth)
            pygame.draw.line(
                screen, (73, 48, 30),
                (tx, tooth_y), (tx, tooth_y + max(2, int(height * 0.12))), 1
            )

    def _draw_gem_badge(self, screen, rect):
        self._frame(screen, rect)
        cx, cy = rect.center
        s = min(rect.width, rect.height) * 0.30
        outer = [
            (cx, int(cy - s * 1.25)),
            (int(cx + s * 0.76), int(cy - s * 0.48)),
            (int(cx + s * 0.72), int(cy + s * 0.47)),
            (cx, int(cy + s * 1.05)),
            (int(cx - s * 0.72), int(cy + s * 0.47)),
            (int(cx - s * 0.76), int(cy - s * 0.48)),
        ]
        pygame.draw.polygon(screen, (255, 189, 73), outer)
        pygame.draw.polygon(screen, (255, 226, 143), outer, 2)
        inner = [
            (cx, int(cy - s * 0.88)),
            (int(cx + s * 0.50), int(cy - s * 0.37)),
            (int(cx + s * 0.42), int(cy + s * 0.38)),
            (cx, int(cy + s * 0.75)),
            (int(cx - s * 0.42), int(cy + s * 0.38)),
            (int(cx - s * 0.50), int(cy - s * 0.37)),
        ]
        pygame.draw.polygon(screen, (233, 83, 26), inner)
        pygame.draw.polygon(
            screen, (255, 177, 54),
            [(cx, int(cy - s * 0.75)),
             (int(cx + s * 0.22), cy),
             (cx, int(cy + s * 0.56)),
             (int(cx - s * 0.18), int(cy - s * 0.05))]
        )
        pygame.draw.line(
            screen, (255, 240, 182),
            (cx, int(cy - s * 0.70)),
            (int(cx - s * 0.20), int(cy - s * 0.10)), 2
        )

    def _draw_rune_badge(self, screen, rect):
        self._frame(screen, rect)
        cx, cy = rect.center
        size = min(rect.width, rect.height) * 0.28
        color = (255, 168, 56)
        points = [
            (cx, int(cy - size)),
            (cx, int(cy + size)),
            (int(cx - size * 0.68), int(cy - size * 0.25)),
            (cx, int(cy + size * 0.06)),
            (int(cx + size * 0.60), int(cy - size * 0.42)),
            (int(cx + size * 0.50), int(cy + size * 0.42)),
        ]
        pygame.draw.lines(screen, color, False, points[:2], 3)
        pygame.draw.lines(screen, self.GOLD_LIGHT, False, points[2:5], 3)
        pygame.draw.line(
            screen, color,
            (int(cx - size * 0.5), int(cy + size * 0.55)),
            (int(cx + size * 0.55), int(cy + size * 0.55)), 2
        )
        pygame.draw.circle(screen, self.GOLD_LIGHT, (cx, int(cy - size)), 2)

    def _draw_heart(self, screen, x, y, size, fill_ratio):
        """Draw a crisp heart pip with support for partially depleted health."""
        points = [
            (x + size // 2, y + size - 3),
            (x + 3, y + size // 2),
            (x + 2, y + size // 3),
            (x + size // 5, y + size // 6),
            (x + size // 3, y + size // 7),
            (x + size // 2, y + size // 3),
            (x + size * 2 // 3, y + size // 7),
            (x + size * 4 // 5, y + size // 6),
            (x + size - 2, y + size // 3),
            (x + size - 3, y + size // 2),
        ]
        points = [(int(px), int(py)) for px, py in points]
        pygame.draw.polygon(screen, (6, 8, 12), [(px + 1, py + 2) for px, py in points])
        pygame.draw.polygon(screen, self.HEART_DARK, points)

        fill_ratio = max(0.0, min(1.0, fill_ratio))
        if fill_ratio > 0:
            pygame.draw.polygon(screen, self.HEART_RED, points)
            if fill_ratio < 1:
                previous_clip = screen.get_clip()
                screen.set_clip(
                    pygame.Rect(
                        x + int(size * fill_ratio),
                        y,
                        size - int(size * fill_ratio),
                        size
                    )
                )
                pygame.draw.polygon(screen, self.HEART_DARK, points)
                screen.set_clip(previous_clip)
            pygame.draw.lines(
                screen, (255, 112, 92), False, points[1:6], 1
            )
        pygame.draw.lines(
            screen, (116, 73, 59), True, points, 1
        )

    def _draw_menu_button(self, screen, rect):
        mouse_pos = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse_pos)
        self._frame(screen, rect, (22, 24, 26) if hover else None)
        dot_color = self.GOLD_LIGHT if hover else self.GOLD
        radius = max(2, rect.width // 19)
        spacing = rect.width // 4
        for row in range(3):
            for column in range(3):
                pygame.draw.circle(
                    screen,
                    dot_color,
                    (
                        rect.x + spacing + column * spacing,
                        rect.y + spacing + row * spacing
                    ),
                    radius
                )

    def _draw_xp_bar(self, screen, rect, player, scale):
        self._frame(screen, rect)
        inset = max(5, int(14 * scale))
        inner = rect.inflate(-inset, -inset)
        inner.height = max(max(5, int(8 * scale)), inner.height)
        inner.centery = rect.centery
        pygame.draw.rect(screen, (4, 8, 12), inner)

        ratio = (
            max(0.0, min(1.0, player.xp / player.xp_to_next_level))
            if player.xp_to_next_level > 0 else 0.0
        )
        fill_width = int(inner.width * ratio)
        if fill_width > 0:
            fill = pygame.Rect(inner.x, inner.y, fill_width, inner.height)
            pygame.draw.rect(screen, (141, 79, 25), fill)
            upper = pygame.Rect(fill.x, fill.y, fill.width, max(2, fill.height // 3))
            pygame.draw.rect(screen, (255, 190, 69), upper)
            pygame.draw.line(
                screen, (255, 223, 127),
                (fill.left, fill.top),
                (max(fill.left, fill.right - 1), fill.top), 1
            )

        # Small rune ticks segment the bar into readable progress milestones.
        for mark in range(1, 5):
            tick_x = inner.x + inner.width * mark // 5
            pygame.draw.line(
                screen, (76, 54, 34),
                (tick_x, inner.y + 1),
                (tick_x, inner.bottom - 1), 1
            )

    def render(self, screen, player, enemies):
        width, height = screen.get_size()
        scale = max(0.65, min(1.0, width / 1600, height / 900))
        u = lambda value: max(1, int(value * scale))

        alive_enemies = sum(not enemy.is_dead() for enemy in enemies)

        # --------------------------------------------------
        # TOP LEFT: WAVE / ENEMY COUNT / EMBLEM
        # --------------------------------------------------
        left_x = u(32)
        top_y = u(25)
        badge_rect = pygame.Rect(left_x, top_y, u(82), u(78))
        info_rect = pygame.Rect(
            left_x + u(57), top_y + u(2), u(246), u(74)
        )
        self._frame(screen, info_rect)
        self._draw_skull_badge(screen, badge_rect)

        wave = self._font(u(20), bold=True).render(
            "WAVE 1 / 4", True, self.GOLD
        )
        enemies_label = self._font(u(15)).render(
            f"ENEMIES: {alive_enemies}", True, self.TEXT
        )
        screen.blit(wave, (info_rect.x + u(61), info_rect.y + u(13)))
        screen.blit(
            enemies_label,
            (info_rect.x + u(61), info_rect.y + u(43))
        )

        # --------------------------------------------------
        # TOP CENTER: HEALTH HEARTS / AWAKENING PROGRESS
        # --------------------------------------------------
        center_x = width // 2
        health_badge = pygame.Rect(
            center_x - u(263), top_y - u(2), u(70), u(70)
        )
        health_panel = pygame.Rect(
            center_x - u(214), top_y + u(3), u(207), u(60)
        )
        self._draw_gem_badge(screen, health_badge)
        self._frame(screen, health_panel)

        health_ratio = (
            max(0.0, min(1.0, player.health / player.max_health))
            if player.max_health > 0 else 0.0
        )
        heart_size = u(27)
        heart_gap = u(9)
        total_hearts_width = heart_size * 4 + heart_gap * 3
        heart_x = health_panel.centerx - total_hearts_width // 2
        heart_y = health_panel.centery - heart_size // 2
        for index in range(4):
            heart_fill = max(0.0, min(1.0, health_ratio * 4 - index))
            self._draw_heart(
                screen,
                heart_x + index * (heart_size + heart_gap),
                heart_y,
                heart_size,
                heart_fill
            )

        rune_badge = pygame.Rect(
            center_x + u(5), top_y - u(2), u(70), u(70)
        )
        xp_panel = pygame.Rect(
            center_x + u(56), top_y + u(3), u(220), u(60)
        )
        self._draw_rune_badge(screen, rune_badge)
        self._draw_xp_bar(screen, xp_panel, player, scale)

        # --------------------------------------------------
        # TOP RIGHT: INVENTORY / MENU BUTTON
        # --------------------------------------------------
        menu_size = u(70)
        self.menu_button_rect = pygame.Rect(
            width - u(42) - menu_size,
            top_y,
            menu_size,
            menu_size
        )
        self._draw_menu_button(screen, self.menu_button_rect)

        # --------------------------------------------------
        # BOTTOM CENTER: FIVE HOTBAR SLOTS
        # --------------------------------------------------
        slot_size = u(72)
        slot_gap = u(9)
        slot_count = 5
        total_width = slot_count * slot_size + (slot_count - 1) * slot_gap
        first_x = (width - total_width) // 2
        slot_y = height - u(110)

        for index in range(slot_count):
            slot_rect = pygame.Rect(
                first_x + index * (slot_size + slot_gap),
                slot_y,
                slot_size,
                slot_size
            )
            self._frame(screen, slot_rect, (7, 13, 19))

    def menu_button_contains(self, position):
        """Return whether a click landed on the HUD inventory/menu button."""
        return self.menu_button_rect.collidepoint(position)
