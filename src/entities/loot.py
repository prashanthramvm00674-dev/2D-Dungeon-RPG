import pygame

from ui.item_icons import draw_item_icon


class Loot:

    def __init__(self, x, y, item):

        # ==================================================
        # POSITION
        # ==================================================

        self.x = x
        self.y = y

        # ==================================================
        # ITEM
        # ==================================================

        self.item = item

        # ==================================================
        # SIZE
        # ==================================================

        self.width = 24
        self.height = 24

        # ==================================================
        # RECT
        # ==================================================

        self.rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )

        # ==================================================
        # VISUAL
        # ==================================================

        self.color = (
            80,
            220,
            100
        )

        # ==================================================
        # STATE
        # ==================================================

        self.is_collected = False

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        player,
        inventory
    ):

        if self.is_collected:
            return True

        # ==================================================
        # CHECK PLAYER COLLISION
        # ==================================================

        if self.rect.colliderect(
            player.rect
        ):

            # ==================================================
            # ADD ITEM TO INVENTORY
            # ==================================================

            added = inventory.add_item(
                self.item,
                1
            )

            # ==================================================
            # PICKUP SUCCESS
            # ==================================================

            if added:

                self.is_collected = True

                return True

        return False

    # ======================================================
    # RENDER
    # ======================================================

    def render(
        self,
        screen,
        camera
    ):

        if self.is_collected:
            return

        screen_rect = camera.apply(self.rect)
        icon_rect = screen_rect.inflate(14, 14)

        # Warm ground halo and a dark pickup shadow make the bottle readable
        # against both torchlit stone and the dungeon's deep blue shadows.
        halo_rect = icon_rect.inflate(8, 4)
        pygame.draw.ellipse(
            screen,
            (35, 19, 19),
            halo_rect.move(0, 3)
        )
        pygame.draw.ellipse(
            screen,
            (108, 58, 34),
            halo_rect,
            2
        )
        pygame.draw.ellipse(
            screen,
            (227, 111, 58),
            halo_rect.inflate(-5, -3),
            1
        )

        # Use the same detailed potion-bottle icon as the inventory instead
        # of a flat green debug square.
        draw_item_icon(
            screen,
            self.item,
            icon_rect
        )

        pygame.draw.circle(
            screen,
            (255, 214, 135),
            (screen_rect.centerx, screen_rect.top - 3),
            2
        )
