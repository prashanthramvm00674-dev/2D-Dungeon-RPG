"""The Ashen Warden, a single friendly character for the first dialogue milestone."""

import math

import pygame


class AshenWarden:
    """A stationary dungeon guide who offers context-sensitive advice."""

    NAME = "ASHEN WARDEN"
    TITLE = "KEEPER OF THE SEALED HALLS"
    INTERACTION_RADIUS = 112

    def __init__(self, x, y):
        # Keep the Warden slightly inset from the tile edges, matching the
        # pixel-art scale of the player while leaving the tile walkable.
        self.rect = pygame.Rect(int(x), int(y), 32, 36)
        self.prompt_font = pygame.font.Font(None, 20)

    def is_in_range(self, player, radius=INTERACTION_RADIUS):
        """Return True when the player is close enough to speak."""
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return dx * dx + dy * dy <= radius * radius

    def dialogue_for(self, wave_manager, quest_manager):
        """Return short, useful dialogue matched to the current run state."""
        if wave_manager.is_victory or quest_manager.completed:
            return (
                "The Ashen Titan has fallen, and the Ember Core is quiet once more.",
                "You have broken the seal's hold on these halls. The dungeon can finally rest.",
                "The Dungeon Purge is complete. Carry its light beyond these walls.",
            )

        if wave_manager.is_intermission:
            next_wave = min(
                wave_manager.current_wave + 1,
                wave_manager.total_waves,
            )
            return (
                "Listen carefully: silence in this place never lasts.",
                f"Wave {next_wave} is gathering beyond the corridors. Use this brief pause to recover.",
                "Keep a potion ready, and never let the creatures surround you.",
            )

        if wave_manager.current_wave == 1:
            return (
                "I am the Ashen Warden, last keeper of the sealed halls.",
                "The Ember Core draws creatures from the dark. Survive all four waves to cleanse this dungeon.",
                "Watch for fallen potions. Press I for your inventory, use 1-5 for the hotbar, and J to track your quest.",
            )

        return (
            f"You have reached wave {wave_manager.current_wave}. The seal is weakening.",
            "Keep moving through the open corridors, and avoid being surrounded by too many enemies.",
            "Use the brief intermission between waves to steady yourself and prepare.",
        )

    def render(self, screen, camera):
        """Draw a compact hooded Warden with muted stone and ember details."""
        rect = camera.apply(self.rect)
        x, y = rect.x, rect.y

        # Ground shadow and layered hooded cloak.
        pygame.draw.ellipse(
            screen, (12, 12, 14),
            pygame.Rect(x - 3, y + 29, 38, 10),
        )
        pygame.draw.polygon(
            screen, (35, 48, 49),
            [
                (x + 8, y + 13), (x + 12, y + 9),
                (x + 22, y + 9), (x + 27, y + 15),
                (x + 30, y + 34), (x + 2, y + 34),
                (x + 5, y + 20),
            ],
        )
        pygame.draw.polygon(
            screen, (83, 91, 82),
            [(x + 8, y + 16), (x + 13, y + 12),
             (x + 18, y + 18), (x + 13, y + 31), (x + 5, y + 31)],
        )
        pygame.draw.polygon(
            screen, (20, 28, 31),
            [(x + 17, y + 17), (x + 25, y + 13),
             (x + 28, y + 31), (x + 17, y + 33)],
        )

        # Hood, pale weathered face, and a narrow warm highlight.
        pygame.draw.polygon(
            screen, (48, 56, 54),
            [(x + 7, y + 12), (x + 10, y + 3),
             (x + 17, y), (x + 25, y + 4),
             (x + 28, y + 13), (x + 22, y + 18),
             (x + 10, y + 17)],
        )
        pygame.draw.rect(
            screen, (174, 143, 103),
            pygame.Rect(x + 12, y + 7, 10, 10),
        )
        pygame.draw.rect(
            screen, (69, 49, 41),
            pygame.Rect(x + 13, y + 12, 8, 3),
        )
        pygame.draw.line(
            screen, (231, 166, 81),
            (x + 11, y + 23), (x + 15, y + 27), 2,
        )
        pygame.draw.line(
            screen, (119, 80, 48),
            (x + 15, y + 27), (x + 20, y + 23), 2,
        )

        # A worn staff marks the character as a guide, not an enemy.
        staff_x = x + 29
        pygame.draw.line(
            screen, (76, 61, 46),
            (staff_x, y + 5), (staff_x, y + 36), 3,
        )
        pygame.draw.line(
            screen, (172, 116, 57),
            (staff_x, y + 4), (staff_x, y + 10), 2,
        )
        pygame.draw.circle(
            screen, (255, 177, 79), (staff_x, y + 4), 3,
        )
        pygame.draw.circle(
            screen, (255, 219, 137), (staff_x, y + 4), 1,
        )

    def render_interaction_prompt(self, screen, camera, player):
        """Draw a crisp E-to-speak prompt in the UI layer when nearby."""
        if not self.is_in_range(player):
            return

        rect = camera.apply(self.rect)
        label = self.prompt_font.render("E  SPEAK", True, (246, 224, 180))
        panel = pygame.Rect(
            rect.centerx - label.get_width() // 2 - 9,
            rect.top - 28,
            label.get_width() + 18,
            23,
        )
        pygame.draw.rect(screen, (9, 14, 19), panel, border_radius=3)
        pygame.draw.rect(screen, (190, 133, 65), panel, 1, border_radius=3)
        screen.blit(
            label,
            (panel.centerx - label.get_width() // 2,
             panel.centery - label.get_height() // 2),
        )
