"""A modal, keyboard-driven dialogue panel styled for the dark-fantasy HUD."""

import pygame


class DialogueUI:
    """Display dialogue one page at a time and pause the world while open."""

    GOLD = (231, 169, 82)
    TEXT = (237, 231, 216)
    MUTED = (161, 170, 176)

    def __init__(self):
        self.visible = False
        self.speaker = ""
        self.lines = ()
        self.line_index = 0
        self.title_font = pygame.font.Font(None, 30)
        self.body_font = pygame.font.Font(None, 27)
        self.small_font = pygame.font.Font(None, 20)

    def open(self, speaker, lines):
        """Open a fresh conversation at its first line."""
        normalized = tuple(str(line).strip() for line in lines if str(line).strip())
        if not normalized:
            self.close()
            return
        self.speaker = str(speaker)
        self.lines = normalized
        self.line_index = 0
        self.visible = True

    def advance(self):
        """Advance a page, closing the panel after the final line."""
        if not self.visible:
            return False
        if self.line_index + 1 < len(self.lines):
            self.line_index += 1
        else:
            self.close()
        return self.visible

    def close(self):
        self.visible = False
        self.speaker = ""
        self.lines = ()
        self.line_index = 0

    @staticmethod
    def _wrap(text, font, max_width):
        words = text.split()
        if not words:
            return [""]
        wrapped = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                wrapped.append(current)
                current = word
        wrapped.append(current)
        return wrapped

    def render(self, screen):
        if not self.visible:
            return

        width, height = screen.get_size()
        panel_width = min(760, width - 32)
        panel_height = min(218, height - 32)
        panel = pygame.Rect(
            (width - panel_width) // 2,
            height - panel_height - max(24, height // 18),
            panel_width,
            panel_height,
        )

        shade = pygame.Surface((width, height), pygame.SRCALPHA)
        shade.fill((2, 4, 8, 90))
        screen.blit(shade, (0, 0))

        pygame.draw.rect(screen, (3, 5, 8), panel.move(4, 5))
        pygame.draw.rect(screen, (11, 17, 23), panel)
        pygame.draw.rect(screen, (107, 76, 43), panel, 3)
        pygame.draw.rect(screen, self.GOLD, panel.inflate(-8, -8), 1)

        speaker = self.title_font.render(self.speaker, True, self.GOLD)
        screen.blit(speaker, (panel.left + 24, panel.top + 18))

        page_text = self.small_font.render(
            f"{self.line_index + 1} / {len(self.lines)}",
            True, self.MUTED,
        )
        screen.blit(
            page_text,
            (panel.right - 24 - page_text.get_width(), panel.top + 24),
        )
        pygame.draw.line(
            screen, (74, 67, 56),
            (panel.left + 24, panel.top + 54),
            (panel.right - 24, panel.top + 54), 1,
        )

        body_lines = self._wrap(
            self.lines[self.line_index],
            self.body_font,
            panel.width - 52,
        )
        y = panel.top + 72
        max_body_lines = max(1, (panel.height - 120) // 30)
        for line in body_lines[:max_body_lines]:
            surface = self.body_font.render(line, True, self.TEXT)
            screen.blit(surface, (panel.left + 25, y))
            y += 30

        footer = self.small_font.render(
            "E / ENTER / SPACE  NEXT      ESC  CLOSE",
            True, self.MUTED,
        )
        screen.blit(
            footer,
            (panel.right - 24 - footer.get_width(), panel.bottom - 28),
        )
