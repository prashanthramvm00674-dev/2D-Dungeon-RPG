class Inventory:

    def __init__(self, max_slots=12):

        self.max_slots = max_slots

        self.slots = [
            None
            for _ in range(self.max_slots)
        ]

    # ==================================================
    # ADD ITEM
    # ==================================================

    def add_item(self, item, quantity=1):

        for slot in self.slots:

            if slot is None:
                continue

            if slot["item"] == item:

                slot["quantity"] += quantity

                return True

        for index in range(self.max_slots):

            if self.slots[index] is None:

                self.slots[index] = {
                    "item": item,
                    "quantity": quantity
                }

                return True

        return False

    # ==================================================
    # REMOVE ITEM
    # ==================================================

    def remove_item(self, item, quantity=1):

        for index in range(self.max_slots):

            slot = self.slots[index]

            if slot is None:
                continue

            if slot["item"] != item:
                continue

            slot["quantity"] -= quantity

            if slot["quantity"] <= 0:

                self.slots[index] = None

            return True

        return False

    # ==================================================
    # HAS ITEM
    # ==================================================

    def has_item(self, item):

        for slot in self.slots:

            if slot is None:
                continue

            if slot["item"] == item:

                return True

        return False

    # ==================================================
    # GET ITEM COUNT
    # ==================================================

    def get_item_count(self, item):

        total = 0

        for slot in self.slots:

            if slot is None:
                continue

            if slot["item"] == item:

                total += slot["quantity"]

        return total

    # ==================================================
    # EMPTY SLOT
    # ==================================================

    def get_empty_slot(self):

        for index in range(self.max_slots):

            if self.slots[index] is None:

                return index

        return -1

    # ==================================================
    # IS FULL
    # ==================================================

    def is_full(self):

        return self.get_empty_slot() == -1

    # ==================================================
    # CLEAR
    # ==================================================

    def clear(self):

        self.slots = [
            None
            for _ in range(self.max_slots)
        ]

    # ==================================================
    # DEBUG
    # ==================================================

    def debug_print(self):

        print("========== INVENTORY ==========")

        for index, slot in enumerate(self.slots):

            if slot is None:

                print(
                    f"Slot {index + 1}: EMPTY"
                )

            else:

                print(
                    f"Slot {index + 1}: "
                    f"{slot['item']} "
                    f"x{slot['quantity']}"
                )

        print("===============================")