import pygame


def draw_item_icon(screen, item, rect):
    """Draw small, readable fantasy item icons without external image assets."""
    if item is None or rect.width < 8 or rect.height < 8:
        return

    cx, cy = rect.center
    scale = min(rect.width, rect.height) / 42.0
    s = lambda value: max(1, int(value * scale))
    outline = (11, 15, 20)
    highlight = (222, 229, 225)

    # Soft shadow makes the item silhouette read against dark inventory slots.
    shadow = pygame.Rect(
        rect.x + rect.width // 4,
        rect.y + int(rect.height * 0.77),
        rect.width // 2,
        max(2, rect.height // 9)
    )
    pygame.draw.ellipse(screen, (3, 6, 10), shadow)

    if item.name == "Health Potion":
        # Stoppered glass vial with red liquid and a bright glass edge.
        bottle = [
            (cx - s(7), cy - s(5)),
            (cx - s(5), cy - s(10)),
            (cx - s(4), cy - s(17)),
            (cx + s(4), cy - s(17)),
            (cx + s(5), cy - s(10)),
            (cx + s(8), cy - s(5)),
            (cx + s(9), cy + s(10)),
            (cx + s(5), cy + s(15)),
            (cx - s(5), cy + s(15)),
            (cx - s(9), cy + s(10)),
        ]
        pygame.draw.polygon(screen, outline, bottle)
        glass = [
            (cx - s(5), cy - s(4)),
            (cx - s(3), cy - s(9)),
            (cx - s(2), cy - s(15)),
            (cx + s(2), cy - s(15)),
            (cx + s(3), cy - s(9)),
            (cx + s(6), cy - s(4)),
            (cx + s(7), cy + s(9)),
            (cx + s(4), cy + s(12)),
            (cx - s(4), cy + s(12)),
            (cx - s(7), cy + s(9)),
        ]
        pygame.draw.polygon(screen, (89, 40, 53), glass)
        pygame.draw.polygon(
            screen,
            (176, 35, 49),
            [
                (cx - s(7), cy + s(2)),
                (cx + s(7), cy + s(2)),
                (cx + s(7), cy + s(9)),
                (cx + s(4), cy + s(12)),
                (cx - s(4), cy + s(12)),
                (cx - s(7), cy + s(9)),
            ]
        )
        pygame.draw.line(
            screen, (255, 99, 92),
            (cx - s(4), cy + s(4)),
            (cx - s(4), cy + s(8)), s(2)
        )
        pygame.draw.line(
            screen, (214, 223, 219),
            (cx - s(6), cy - s(4)),
            (cx - s(5), cy + s(5)), s(2)
        )
        pygame.draw.rect(
            screen, outline,
            pygame.Rect(cx - s(6), cy - s(22), s(12), s(6))
        )
        pygame.draw.rect(
            screen, (176, 119, 48),
            pygame.Rect(cx - s(5), cy - s(21), s(10), s(3))
        )
        pygame.draw.line(
            screen, (255, 215, 115),
            (cx - s(4), cy - s(20)),
            (cx + s(3), cy - s(20)), 1
        )

    elif item.name == "Iron Sword":
        # Dark outline, bright steel blade, crossguard, and leather grip.
        blade = [
            (cx + s(1), cy - s(18)),
            (cx + s(7), cy - s(23)),
            (cx + s(5), cy - s(14)),
            (cx - s(5), cy + s(2)),
            (cx - s(9), cy - s(1)),
        ]
        pygame.draw.polygon(screen, outline, blade)
        pygame.draw.polygon(
            screen, (151, 173, 184),
            [
                (cx + s(2), cy - s(17)),
                (cx + s(6), cy - s(21)),
                (cx + s(4), cy - s(14)),
                (cx - s(5), cy + s(1)),
                (cx - s(7), cy - s(1)),
            ]
        )
        pygame.draw.line(
            screen, highlight,
            (cx + s(4), cy - s(17)),
            (cx + s(5), cy - s(20)), 1
        )
        pygame.draw.line(
            screen, outline,
            (cx - s(11), cy - s(1)),
            (cx - s(3), cy + s(5)), s(4)
        )
        pygame.draw.line(
            screen, (190, 137, 59),
            (cx - s(11), cy - s(1)),
            (cx - s(3), cy + s(5)), s(2)
        )
        pygame.draw.line(
            screen, outline,
            (cx - s(10), cy - s(2)),
            (cx - s(1), cy + s(7)), s(4)
        )
        pygame.draw.line(
            screen, (176, 190, 194),
            (cx - s(12), cy - s(3)),
            (cx - s(1), cy + s(8)), s(2)
        )
        pygame.draw.line(
            screen, (84, 50, 32),
            (cx - s(3), cy + s(7)),
            (cx - s(8), cy + s(13)), s(4)
        )
        pygame.draw.line(
            screen, (199, 153, 78),
            (cx - s(5), cy + s(5)),
            (cx - s(9), cy + s(10)), 1
        )

    elif item.name == "Shield":
        # Layered heater shield with brass trim and a raised central boss.
        shield = [
            (cx, cy - s(20)),
            (cx + s(14), cy - s(15)),
            (cx + s(12), cy + s(3)),
            (cx + s(7), cy + s(13)),
            (cx, cy + s(19)),
            (cx - s(7), cy + s(13)),
            (cx - s(12), cy + s(3)),
            (cx - s(14), cy - s(15)),
        ]
        pygame.draw.polygon(screen, outline, shield)
        pygame.draw.polygon(screen, (170, 112, 45), [
            (cx, cy - s(18)),
            (cx + s(12), cy - s(14)),
            (cx + s(10), cy + s(2)),
            (cx + s(5), cy + s(11)),
            (cx, cy + s(16)),
            (cx - s(5), cy + s(11)),
            (cx - s(10), cy + s(2)),
            (cx - s(12), cy - s(14)),
        ])
        pygame.draw.polygon(screen, (42, 74, 99), [
            (cx, cy - s(15)),
            (cx + s(9), cy - s(12)),
            (cx + s(7), cy + s(2)),
            (cx, cy + s(12)),
            (cx - s(7), cy + s(2)),
            (cx - s(9), cy - s(12)),
        ])
        pygame.draw.line(
            screen, (111, 171, 197),
            (cx, cy - s(13)), (cx, cy + s(11)), s(2)
        )
        pygame.draw.line(
            screen, (245, 201, 112),
            (cx - s(8), cy - s(10)), (cx + s(8), cy - s(10)), 1
        )
        pygame.draw.polygon(
            screen, (223, 175, 74),
            [
                (cx, cy - s(6)), (cx + s(4), cy),
                (cx, cy + s(6)), (cx - s(4), cy)
            ]
        )
        pygame.draw.polygon(
            screen, (255, 226, 151),
            [
                (cx, cy - s(4)), (cx + s(2), cy),
                (cx, cy + s(3)), (cx - s(2), cy)
            ]
        )

    else:
        # Unknown future items still get a visible framed token.
        token = pygame.Rect(
            cx - s(12), cy - s(12), s(24), s(24)
        )
        pygame.draw.rect(screen, outline, token)
        pygame.draw.rect(screen, (162, 173, 181), token.inflate(-s(4), -s(4)), 2)
        pygame.draw.circle(screen, (235, 190, 91), (cx, cy), s(4))
