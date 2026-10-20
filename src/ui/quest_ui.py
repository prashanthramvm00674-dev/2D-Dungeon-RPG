"""Readable quest journal overlay; leaves the gameplay HUD untouched."""

import pygame


class QuestJournalUI:
    """A lightweight, keyboard-toggled journal for the main dungeon quest."""

    GOLD = (224, 170, 83)
    TEXT = (235, 230, 218)
    MUTED = (164, 166, 171)
    GREEN = (132, 207, 143)

    def __init__(self):
        self.visible = False
        self.title_font = pygame.font.Font(None, 42)
        self.heading_font = pygame.font.Font(None, 29)
        self.body_font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 21)

    def toggle(self):
        self.visible = not self.visible

    def close(self):
        self.visible = False

    def render(self, screen, quest, wave_manager, alive_count):
        if not self.visible:
            return

        width, height = screen.get_size()
        panel_width = min(640, width - 32)
        panel_height = min(390, height - 32)
        panel = pygame.Rect(
            (width - panel_width) // 2,
            (height - panel_height) // 2,
            panel_width,
            panel_height,
        )

        shade = pygame.Surface((width, height), pygame.SRCALPHA)
        shade.fill((3, 5, 9, 178))
        screen.blit(shade, (0, 0))

        card = pygame.Surface(panel.size, pygame.SRCALPHA)
        card.fill((12, 17, 24, 247))
        screen.blit(card, panel.topleft)
        pygame.draw.rect(screen, (91, 69, 44), panel, 2)
        pygame.draw.rect(screen, self.GOLD, panel.inflate(-8, -8), 1)

        left = panel.x + 30
        top = panel.y + 24

        title = self.title_font.render("QUEST JOURNAL", True, self.GOLD)
        screen.blit(title, (left, top))

        snapshot = quest.progress(wave_manager, alive_count)
        state_label = "COMPLETED" if snapshot["completed"] else "IN PROGRESS"
        state_color = self.GREEN if snapshot["completed"] else self.GOLD
        state = self.small_font.render(state_label, True, state_color)
        screen.blit(state, (panel.right - 30 - state.get_width(), top + 10))

        divider_y = top + 48
        pygame.draw.line(
            screen, (83, 73, 59),
            (left, divider_y), (panel.right - 30, divider_y), 1
        )

        quest_name = self.heading_font.render(
            snapshot["name"], True, self.TEXT
        )
        screen.blit(quest_name, (left, divider_y + 22))

        description = self.body_font.render(
            snapshot["description"], True, self.MUTED
        )
        screen.blit(description, (left, divider_y + 62))

        progress_y = divider_y + 112
        progress_label = self.body_font.render(
            f"Wave {snapshot['current_wave']} / {snapshot['total_waves']}",
            True, self.TEXT
        )
        screen.blit(progress_label, (left, progress_y))

        enemies_label = self.body_font.render(
            f"Enemies remaining: {snapshot['enemies_remaining']}",
            True, self.TEXT
        )
        screen.blit(enemies_label, (left, progress_y + 34))

        reward_y = progress_y + 86
        reward_label = self.body_font.render(
            f"Completion reward: +{snapshot['reward_xp']} XP",
            True, self.GREEN if snapshot["completed"] else self.GOLD
        )
        screen.blit(reward_label, (left, reward_y))

        if snapshot["completed"]:
            footer_text = "The dungeon is clear. Your reward has been granted."
            footer_color = self.GREEN
        else:
            footer_text = "Finish the remaining waves to complete this quest."
            footer_color = self.MUTED
        footer = self.small_font.render(footer_text, True, footer_color)
        screen.blit(footer, (left, panel.bottom - 52))

        hint = self.small_font.render("J / ESC  -  CLOSE", True, self.MUTED)
        screen.blit(
            hint,
            (panel.right - 30 - hint.get_width(), panel.bottom - 28)
        )
