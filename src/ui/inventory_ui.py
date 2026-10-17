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

        self.button_font = pygame.font.Font(
            None,
            22
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
    # CHECK EQUIPPED
    # ==================================================

    def is_equipped(
        self,
        item,
        player
    ):

        if item is None:
            return False

        if item.item_type == "weapon":

            return (
                player.equipped_weapon == item
            )

        if item.item_type == "armor":

            return (
                player.equipped_shield == item
            )

        return False

    # ==================================================
    # EQUIP / UNEQUIP
    # ==================================================

    def equip_or_unequip(
        self,
        item,
        player
    ):

        if item is None:
            return

        # --------------------------------------------------
        # WEAPON
        # --------------------------------------------------

        if item.item_type == "weapon":

            if player.equipped_weapon == item:

                player.unequip_weapon()

            else:

                player.equip_item(
                    item
                )

        # --------------------------------------------------
        # ARMOR / SHIELD
        # --------------------------------------------------

        elif item.item_type == "armor":

            if player.equipped_shield == item:

                player.unequip_shield()

            else:

                player.equip_item(
                    item
                )

    # ==================================================
    # USE ITEM
    # ==================================================

    def use_item(
        self,
        item,
        player,
        inventory
    ):

        if item is None:
            return False

        # --------------------------------------------------
        # HEALTH POTION
        # --------------------------------------------------

        if item.item_type == "consumable":

            if item.name == "Health Potion":

                if player.health >= player.max_health:

                    return False

                heal_amount = min(
                    item.value,
                    player.max_health
                    - player.health
                )

                player.health += heal_amount

                inventory.remove_item(
                    item,
                    1
                )

                return True

        return False

    # ==================================================
    # HANDLE KEY
    # ==================================================

    def handle_key(
        self,
        key,
        inventory,
        player
    ):

        if not self.visible:

            return

        # ==================================================
        # CLOSE
        # ==================================================

        if key == pygame.K_i:

            self.close()

            return

        if key == pygame.K_ESCAPE:

            self.close()

            return

        # ==================================================
        # SELECT NEXT ITEM
        # ==================================================

        if key == pygame.K_RIGHT:

            self.select_next(
                inventory
            )

            return

        # ==================================================
        # SELECT PREVIOUS ITEM
        # ==================================================

        if key == pygame.K_LEFT:

            self.select_previous(
                inventory
            )

            return

        # ==================================================
        # SELECT DOWN
        # ==================================================

        if key == pygame.K_DOWN:

            self.select_down(
                inventory
            )

            return

        # ==================================================
        # SELECT UP
        # ==================================================

        if key == pygame.K_UP:

            self.select_up(
                inventory
            )

            return

        # ==================================================
        # GET SELECTED ITEM
        # ==================================================

        if (
            self.selected_slot < 0
            or self.selected_slot
            >= inventory.max_slots
        ):

            return

        slot = inventory.slots[
            self.selected_slot
        ]

        if slot is None:

            return

        item = slot["item"]

        # ==================================================
        # USE
        # ==================================================

        if key == pygame.K_u:

            self.use_item(
                item,
                player,
                inventory
            )

            return

        # ==================================================
        # EQUIP
        # ==================================================

        if key == pygame.K_e:

            if (
                item.item_type == "weapon"
                or item.item_type == "armor"
            ):

                self.equip_or_unequip(
                    item,
                    player
                )

    # ==================================================
    # SELECT NEXT
    # ==================================================

    def select_next(
        self,
        inventory
    ):

        if inventory.max_slots <= 0:

            return

        if self.selected_slot < 0:

            self.selected_slot = 0

            return

        self.selected_slot += 1

        if (
            self.selected_slot
            >= inventory.max_slots
        ):

            self.selected_slot = 0

    # ==================================================
    # SELECT PREVIOUS
    # ==================================================

    def select_previous(
        self,
        inventory
    ):

        if inventory.max_slots <= 0:

            return

        if self.selected_slot < 0:

            self.selected_slot = (
                inventory.max_slots - 1
            )

            return

        self.selected_slot -= 1

        if self.selected_slot < 0:

            self.selected_slot = (
                inventory.max_slots - 1
            )

    # ==================================================
    # SELECT DOWN
    # ==================================================

    def select_down(
        self,
        inventory
    ):

        columns = 4

        if self.selected_slot < 0:

            self.selected_slot = 0

            return

        new_slot = (
            self.selected_slot
            + columns
        )

        if (
            new_slot
            < inventory.max_slots
        ):

            self.selected_slot = new_slot

    # ==================================================
    # SELECT UP
    # ==================================================

    def select_up(
        self,
        inventory
    ):

        columns = 4

        if self.selected_slot < 0:

            self.selected_slot = 0

            return

        new_slot = (
            self.selected_slot
            - columns
        )

        if new_slot >= 0:

            self.selected_slot = new_slot

    # ==================================================
    # RESPONSIVE LAYOUT
    # ==================================================

    def _calculate_layout(self, screen_size):
        """Calculate inventory geometry from the current window size."""
        screen_width, screen_height = screen_size

        panel_width = 620
        panel_height = 500

        panel_x = max(0, (screen_width - panel_width) // 2)
        panel_y = max(0, (screen_height - panel_height) // 2)
        panel = pygame.Rect(
            panel_x,
            panel_y,
            panel_width,
            panel_height
        )

        return {
            "panel": panel,
            "slot_start_x": panel.left + 50,
            "slot_start_y": panel.top + 80,
            "slot_size": 70,
            "gap": 10,
            "columns": 4,
            "button_rect": pygame.Rect(
                panel.left + 330,
                panel.top + 410,
                220,
                45
            ),
        }

    # ==================================================
    # HANDLE CLICK
    # ==================================================

    def handle_click(
        self,
        mouse_position,
        inventory,
        player,
        screen_size=None
    ):

        if not self.visible:

            return

        mouse_x, mouse_y = mouse_position

        # ==================================================
        # INVENTORY SLOTS
        # ==================================================

        if screen_size is None:
            screen_size = getattr(
                self,
                "_last_screen_size",
                (1920, 1080)
            )

        layout = self._calculate_layout(screen_size)
        start_x = layout["slot_start_x"]
        start_y = layout["slot_start_y"]
        slot_size = layout["slot_size"]
        gap = layout["gap"]
        columns = layout["columns"]

        for index in range(
            inventory.max_slots
        ):

            row = index // columns
            column = index % columns

            x = (
                start_x
                + column
                * (slot_size + gap)
            )

            y = (
                start_y
                + row
                * (slot_size + gap)
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

                # ==================================================
                # CONSUMABLE
                # ==================================================

                if item.item_type == "consumable":

                    self.use_item(
                        item,
                        player,
                        inventory
                    )

                # ==================================================
                # EQUIPMENT
                # ==================================================

                elif (
                    item.item_type == "weapon"
                    or item.item_type == "armor"
                ):

                    self.equip_or_unequip(
                        item,
                        player
                    )

                return

        # ==================================================
        # EQUIP BUTTON
        # ==================================================

        button_rect = layout["button_rect"]

        if button_rect.collidepoint(
            mouse_x,
            mouse_y
        ):

            if (
                self.selected_slot >= 0
                and self.selected_slot
                < inventory.max_slots
            ):

                slot = inventory.slots[
                    self.selected_slot
                ]

                if slot is not None:

                    item = slot["item"]

                    if (
                        item.item_type == "weapon"
                        or item.item_type == "armor"
                    ):

                        self.equip_or_unequip(
                            item,
                            player
                        )

    # ==================================================
    # RENDER
    # ==================================================

    def render(
        self,
        screen,
        inventory,
        player
    ):

        if not self.visible:

            return

        self._last_screen_size = screen.get_size()
        layout = self._calculate_layout(self._last_screen_size)
        panel = layout["panel"]

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

        panel = layout["panel"]

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
                panel.top + 25
            )
        )

        # ==================================================
        # SLOTS
        # ==================================================

        start_x = layout["slot_start_x"]
        start_y = layout["slot_start_y"]
        slot_size = layout["slot_size"]
        gap = layout["gap"]
        columns = layout["columns"]

        for index in range(
            inventory.max_slots
        ):

            row = index // columns
            column = index % columns

            x = (
                start_x
                + column
                * (slot_size + gap)
            )

            y = (
                start_y
                + row
                * (slot_size + gap)
            )

            rect = pygame.Rect(
                x,
                y,
                slot_size,
                slot_size
            )

            # ==================================================
            # SELECTED
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

            if slot is None:

                continue

            item = slot["item"]

            quantity = slot["quantity"]

            # ==================================================
            # ITEM NAME
            # ==================================================

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

            # ==================================================
            # QUANTITY
            # ==================================================

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
            # EQUIPPED
            # ==================================================

            if self.is_equipped(
                item,
                player
            ):

                equipped_text = (
                    self.small_font.render(
                        "EQUIPPED",
                        True,
                        (100, 255, 120)
                    )
                )

                screen.blit(
                    equipped_text,
                    (
                        x + 3,
                        y - 17
                    )
                )

        # ==================================================
        # SELECTED ITEM INFORMATION
        # ==================================================

        selected_item = None

        if (
            self.selected_slot >= 0
            and self.selected_slot
            < inventory.max_slots
        ):

            selected = inventory.slots[
                self.selected_slot
            ]

            if selected is not None:

                selected_item = selected["item"]

        if selected_item is not None:

            # ==================================================
            # DESCRIPTION
            # ==================================================

            info_text = self.info_font.render(
                selected_item.description,
                True,
                (220, 220, 220)
            )

            screen.blit(
                info_text,
                (
                    panel.left + 25,
                    panel.top + 380
                )
            )

            # ==================================================
            # EQUIPMENT BUTTON
            # ==================================================

            if (
                selected_item.item_type == "weapon"
                or selected_item.item_type == "armor"
            ):

                if self.is_equipped(
                    selected_item,
                    player
                ):

                    button_text_value = "UNEQUIP"

                else:

                    button_text_value = "EQUIP"

                button_rect = layout["button_rect"]

                pygame.draw.rect(
                    screen,
                    (65, 85, 100),
                    button_rect
                )

                pygame.draw.rect(
                    screen,
                    (180, 180, 190),
                    button_rect,
                    2
                )

                button_text = (
                    self.button_font.render(
                        button_text_value,
                        True,
                        (255, 255, 255)
                    )
                )

                screen.blit(
                    button_text,
                    (
                        button_rect.centerx
                        - button_text.get_width()
                        // 2,
                        button_rect.centery
                        - button_text.get_height()
                        // 2
                    )
                )

            # ==================================================
            # CONSUMABLE BUTTON
            # ==================================================

            elif selected_item.item_type == "consumable":

                button_rect = layout["button_rect"]

                pygame.draw.rect(
                    screen,
                    (65, 100, 75),
                    button_rect
                )

                pygame.draw.rect(
                    screen,
                    (180, 180, 190),
                    button_rect,
                    2
                )

                button_text = (
                    self.button_font.render(
                        "USE  [U]",
                        True,
                        (255, 255, 255)
                    )
                )

                screen.blit(
                    button_text,
                    (
                        button_rect.centerx
                        - button_text.get_width()
                        // 2,
                        button_rect.centery
                        - button_text.get_height()
                        // 2
                    )
                )

        # ==================================================
        # CONTROLS
        # ==================================================

        controls_text = self.small_font.render(
            "ARROWS SELECT   U USE   E EQUIP",
            True,
            (180, 180, 180)
        )

        screen.blit(
            controls_text,
            (
                panel.centerx
                - controls_text.get_width() // 2,
                panel.top + 440
            )
        )

        # ==================================================
        # CLOSE
        # ==================================================

        close_text = self.small_font.render(
            "I / ESC - CLOSE",
            True,
            (200, 200, 200)
        )

        screen.blit(
            close_text,
            (
                panel.centerx
                - close_text.get_width() // 2,
                panel.top + 465
            )
        )