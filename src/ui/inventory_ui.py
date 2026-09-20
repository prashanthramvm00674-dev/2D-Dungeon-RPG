import pygame


class InventoryUI:

    def __init__(self):

        self.visible = False

        self.selected_slot = -1

        self.font = pygame.font.Font(
            None,
            24
        )

        self.small_font = pygame.font.Font(
            None,
            18
        )

        self.info_font = pygame.font.Font(
            None,
            20
        )

    # ==================================================
    # TOGGLE
    # ==================================================

    def toggle(self):

        self.visible = not self.visible

        self.selected_slot = -1

    # ==================================================
    # CLOSE
    # ==================================================

    def close(self):

        self.visible = False

        self.selected_slot = -1

    # ==================================================
    # HANDLE CLICK
    # ==================================================

    def handle_click(
        self,
        mouse_position,
        inventory,
        player
    ):

        if not self.visible:

            return

        mouse_x, mouse_y = mouse_position

        start_x = 220
        start_y = 170

        slot_size = 70
        gap = 10

        columns = 4

        for index in range(
            inventory.max_slots
        ):

            row = index // columns
            column = index % columns

            x = (
                start_x
                + column * (slot_size + gap)
            )

            y = (
                start_y
                + row * (slot_size + gap)
            )

            rect = pygame.Rect(
                x,
                y,
                slot_size,
                slot_size
            )

            if rect.collidepoint(
                mouse_x,
                mouse_y
            ):

                self.selected_slot = index

                slot = inventory.slots[index]

                if slot is None:

                    return

                item = slot["item"]

                # ==========================================
                # HEALTH POTION
                # ==========================================

                if item.item_type == "consumable":

                    if item.name == "Health Potion":

                        # Don't use potion at full health
                        if player.health >= player.max_health:

                            return

                        heal_amount = min(
                            item.value,
                            player.max_health - player.health
                        )

                        player.health += heal_amount

                        inventory.remove_item(
                            item,
                            1
                        )

                return

    # ==================================================
    # RENDER
    # ==================================================

    def render(
        self,
        screen,
        inventory
    ):

        if not self.visible:

            return

        # ==================================================
        # DARK OVERLAY
        # ==================================================

        overlay = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 170)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        # ==================================================
        # PANEL
        # ==================================================

        panel = pygame.Rect(
            170,
            90,
            620,
            500
        )

        pygame.draw.rect(
            screen,
            (35, 35, 45),
            panel
        )

        pygame.draw.rect(
            screen,
            (150, 150, 160),
            panel,
            3
        )

        # ==================================================
        # TITLE
        # ==================================================

        title = self.font.render(
            "INVENTORY",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (
                panel.centerx
                - title.get_width() // 2,
                115
            )
        )

        # ==================================================
        # SLOTS
        # ==================================================

        start_x = 220
        start_y = 170

        slot_size = 70
        gap = 10

        columns = 4

        for index in range(
            inventory.max_slots
        ):

            row = index // columns
            column = index % columns

            x = (
                start_x
                + column * (slot_size + gap)
            )

            y = (
                start_y
                + row * (slot_size + gap)
            )

            rect = pygame.Rect(
                x,
                y,
                slot_size,
                slot_size
            )

            # ==================================================
            # SLOT BACKGROUND
            # ==================================================

            if index == self.selected_slot:

                pygame.draw.rect(
                    screen,
                    (220, 190, 70),
                    rect
                )

            else:

                pygame.draw.rect(
                    screen,
                    (55, 55, 65),
                    rect
                )

            pygame.draw.rect(
                screen,
                (150, 150, 160),
                rect,
                2
            )

            # ==================================================
            # ITEM
            # ==================================================

            slot = inventory.slots[index]

            if slot is not None:

                item = slot["item"]

                quantity = slot["quantity"]

                # ------------------------------------------
                # ITEM NAME
                # ------------------------------------------

                item_text = self.small_font.render(
                    item.name,
                    True,
                    (255, 255, 255)
                )

                screen.blit(
                    item_text,
                    (
                        x + 5,
                        y + 8
                    )
                )

                # ------------------------------------------
                # QUANTITY
                # ------------------------------------------

                quantity_text = self.small_font.render(
                    f"x{quantity}",
                    True,
                    (255, 220, 100)
                )

                screen.blit(
                    quantity_text,
                    (
                        x + 5,
                        y + 45
                    )
                )

        # ==================================================
        # SELECTED ITEM INFORMATION
        # ==================================================

        if (
            self.selected_slot >= 0
            and self.selected_slot < inventory.max_slots
        ):

            selected = inventory.slots[
                self.selected_slot
            ]

            if selected is not None:

                item = selected["item"]

                info_text = self.info_font.render(
                    item.description,
                    True,
                    (220, 220, 220)
                )

                screen.blit(
                    info_text,
                    (
                        panel.left + 25,
                        510
                    )
                )

        # ==================================================
        # CLOSE TEXT
        # ==================================================

        close_text = self.small_font.render(
            "I - CLOSE",
            True,
            (200, 200, 200)
        )

        screen.blit(
            close_text,
            (
                panel.centerx
                - close_text.get_width() // 2,
                555
            )
        )