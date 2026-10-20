import pygame

from ui.item_icons import draw_item_icon


class InventoryUI:

    def __init__(self):

        self.visible = False

        self.selected_slot = -1
        self.hovered_slot = -1

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
        self.item_label_font = pygame.font.Font(None, 15)
        self.quantity_font = pygame.font.Font(None, 18)
        self.equipped_font = pygame.font.Font(None, 14)

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
                panel.top + 370,
                220,
                45
            ),
        }

    def _slot_rect(self, index, layout):
        """Return the exact on-screen rectangle used to draw and click a slot."""
        row = index // layout["columns"]
        column = index % layout["columns"]
        slot_size = layout["slot_size"]
        gap = layout["gap"]
        return pygame.Rect(
            layout["slot_start_x"] + column * (slot_size + gap),
            layout["slot_start_y"] + row * (slot_size + gap),
            slot_size,
            slot_size
        )

    def activate_item(self, item, player, inventory):
        """Activate a selected item from a mouse double-click."""
        if item is None:
            return False

        if item.item_type == "consumable":
            return self.use_item(item, player, inventory)

        if item.item_type in ("weapon", "armor"):
            self.equip_or_unequip(item, player)
            return True

        return False

    # ==================================================
    # HANDLE CLICK
    # ==================================================

    def handle_click(
        self,
        mouse_position,
        inventory,
        player,
        screen_size=None,
        click_count=1
    ):
        """Handle inventory slot selection and mouse-accessible item actions."""
        if not self.visible:
            return False

        if screen_size is None:
            screen_size = getattr(
                self,
                "_last_screen_size",
                (1920, 1080)
            )

        layout = self._calculate_layout(screen_size)
        mouse_x, mouse_y = mouse_position

        # Slot drawing and hit testing share the same geometry. The small
        # tolerance includes the visible metal edge and its drop shadow.
        for index in range(inventory.max_slots):
            rect = self._slot_rect(index, layout)
            if rect.inflate(8, 8).collidepoint(mouse_x, mouse_y):
                self.selected_slot = index
                slot = inventory.slots[index]

                if slot is not None and click_count >= 2:
                    self.activate_item(
                        slot["item"],
                        player,
                        inventory
                    )
                return True

        # The action button is also a full mouse target. A single click on a
        # slot selects it; the button performs USE/EQUIP, and double-clicking
        # a populated slot performs the same primary action directly.
        button_rect = layout["button_rect"]
        if button_rect.collidepoint(mouse_x, mouse_y):
            if 0 <= self.selected_slot < inventory.max_slots:
                slot = inventory.slots[self.selected_slot]
                if slot is not None:
                    self.activate_item(slot["item"], player, inventory)
            return True

        return False

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
            (5, 9, 14),
            panel.inflate(8, 8)
        )
        pygame.draw.rect(
            screen,
            (12, 18, 25),
            panel
        )
        pygame.draw.rect(
            screen,
            (150, 94, 48),
            panel,
            3
        )
        pygame.draw.rect(
            screen,
            (232, 170, 82),
            panel.inflate(-8, -8),
            1
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
        self.hovered_slot = -1
        mouse_position = pygame.mouse.get_pos()

        for index in range(
            inventory.max_slots
        ):

            rect = self._slot_rect(index, layout)
            x, y = rect.topleft
            hovered = rect.inflate(8, 8).collidepoint(
                pygame.mouse.get_pos()
            )
            if hovered:
                self.hovered_slot = index

            # ==================================================
            # SELECTED
            # ==================================================

            pygame.draw.rect(
                screen,
                (49, 41, 27) if index == self.selected_slot else ((34, 40, 46) if hovered else (16, 25, 34)),
                rect
            )
            pygame.draw.rect(
                screen,
                (246, 190, 91) if index == self.selected_slot else ((171, 186, 194) if hovered else (120, 83, 45)),
                rect,
                2
            )
            pygame.draw.rect(
                screen,
                (89, 100, 105) if index == self.selected_slot else (38, 52, 63),
                rect.inflate(-6, -6),
                1
            )

            # ==================================================
            # ITEM
            # ==================================================

            slot = inventory.slots[index]

            if slot is None:

                continue

            item = slot["item"]

            quantity = slot["quantity"]

            # Item icon is the primary visual signal; compact labels stay
            # inside the slot at all supported display resolutions.
            icon_rect = pygame.Rect(
                x + 13,
                y + 5,
                slot_size - 26,
                37
            )
            draw_item_icon(screen, item, icon_rect)

            label_by_name = {
                "Health Potion": "POTION",
                "Iron Sword": "IRON SWORD",
                "Shield": "SHIELD",
            }
            label = label_by_name.get(item.name, item.name.upper())
            item_text = self.item_label_font.render(
                label,
                True,
                (232, 225, 208)
            )
            screen.blit(
                item_text,
                (
                    rect.centerx - item_text.get_width() // 2,
                    y + 48
                )
            )

            quantity_text = self.quantity_font.render(
                f"x{quantity}",
                True,
                (255, 215, 126)
            )
            quantity_bg = pygame.Rect(
                rect.right - quantity_text.get_width() - 5,
                y + 30,
                quantity_text.get_width() + 4,
                15
            )
            pygame.draw.rect(screen, (6, 11, 16), quantity_bg)
            screen.blit(
                quantity_text,
                (quantity_bg.x + 2, quantity_bg.y - 1)
            )

            # ==================================================
            # EQUIPPED
            # ==================================================

            if self.is_equipped(
                item,
                player
            ):

                equipped_text = self.equipped_font.render(
                    "EQUIPPED",
                    True,
                    (127, 235, 135)
                )
                badge = pygame.Rect(
                    rect.centerx - equipped_text.get_width() // 2 - 3,
                    y - 17,
                    equipped_text.get_width() + 6,
                    15
                )
                pygame.draw.rect(screen, (7, 18, 13), badge)
                screen.blit(
                    equipped_text,
                    (badge.x + 3, badge.y)
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
                    panel.top + 330
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
            "CLICK / ARROWS SELECT    U USE    E EQUIP    I / ESC CLOSE",
            True,
            (198, 177, 139)
        )

        screen.blit(
            controls_text,
            (
                panel.centerx
                - controls_text.get_width() // 2,
                panel.top + 430
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
                panel.top + 460
            )
        )