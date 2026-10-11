import pygame


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

        screen_rect = camera.apply(
            self.rect
        )

        pygame.draw.rect(
            screen,
            self.color,
            screen_rect
        )

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            screen_rect,
            2
        )