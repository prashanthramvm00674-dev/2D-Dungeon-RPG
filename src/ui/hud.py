import pygame


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

    def render(self, screen, player, enemies):

        # ==================================================
        # PLAYER HUD — TOP LEFT
        # ==================================================

        player_panel = pygame.Rect(
            15,
            15,
            280,
            115
        )

        pygame.draw.rect(
            screen,
            (25, 25, 30),
            player_panel
        )

        pygame.draw.rect(
            screen,
            (80, 80, 90),
            player_panel,
            2
        )

        # -------------------------
        # HP LABEL
        # -------------------------

        hp_text = self.font.render(
            "HP",
            True,
            (255, 255, 255)
        )

        screen.blit(
            hp_text,
            (30, 27)
        )

        # -------------------------
        # HP BAR
        # -------------------------

        bar_x = 65
        bar_y = 30
        bar_width = 200
        bar_height = 18

        health_ratio = (
            player.health / player.max_health
        )

        background = pygame.Rect(
            bar_x,
            bar_y,
            bar_width,
            bar_height
        )

        health = pygame.Rect(
            bar_x,
            bar_y,
            int(bar_width * health_ratio),
            bar_height
        )

        pygame.draw.rect(
            screen,
            (60, 60, 65),
            background
        )

        pygame.draw.rect(
            screen,
            (50, 190, 80),
            health
        )

        pygame.draw.rect(
            screen,
            (150, 150, 160),
            background,
            2
        )

        # -------------------------
        # HP NUMBER
        # -------------------------

        hp_number = self.small_font.render(
            f"{player.health}/{player.max_health}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            hp_number,
            (
                bar_x
                + bar_width // 2
                - hp_number.get_width() // 2,
                bar_y - 1
            )
        )

        # -------------------------
        # ATTACK STATUS
        # -------------------------

        if player.is_attacking:

            attack_text = self.small_font.render(
                "ATTACK: ATTACKING",
                True,
                (255, 100, 100)
            )

        else:

            attack_text = self.small_font.render(
                "ATTACK: READY",
                True,
                (120, 220, 120)
            )

        screen.blit(
            attack_text,
            (30, 95)
        )

        # ==================================================
        # DUNGEON STATUS — TOP RIGHT
        # ==================================================

        alive_enemies = sum(
            not enemy.is_dead()
            for enemy in enemies
        )

        panel_width = 240
        panel_height = 90

        panel_x = (
            screen.get_width()
            - panel_width
            - 15
        )

        panel_y = 15

        dungeon_panel = pygame.Rect(
            panel_x,
            panel_y,
            panel_width,
            panel_height
        )

        pygame.draw.rect(
            screen,
            (25, 25, 30),
            dungeon_panel
        )

        pygame.draw.rect(
            screen,
            (80, 80, 90),
            dungeon_panel,
            2
        )

        # -------------------------
        # DUNGEON TITLE
        # -------------------------

        title = self.font.render(
            "DUNGEON",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (
                panel_x + 15,
                panel_y + 12
            )
        )

        # -------------------------
        # ENEMY COUNT
        # -------------------------

        enemy_text = self.small_font.render(
            f"ENEMIES: {alive_enemies}",
            True,
            (220, 100, 100)
        )

        screen.blit(
            enemy_text,
            (
                panel_x + 15,
                panel_y + 48
            )
        )

        # -------------------------
        # WAVE
        # -------------------------

        wave_text = self.small_font.render(
            "WAVE: 1",
            True,
            (220, 220, 120)
        )

        screen.blit(
            wave_text,
            (
                panel_x + 140,
                panel_y + 48
            )
        )