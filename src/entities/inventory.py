
class Inventory:
    def __init__(self, max_slots=12):
        self.max_slots = max_slots
        self.slots = [None for _ in range(self.max_slots)]

    def add_item(self, item, quantity=1):
        if quantity <= 0:
            return False

        # Stack existing items when allowed.
        if getattr(item, "stackable", True):
            for slot in self.slots:
                if slot is None:
                    continue

                if slot["item"] == item:
                    slot["quantity"] += quantity
                    return True

        # Otherwise, use an empty slot.
        for index in range(self.max_slots):
            if self.slots[index] is None:
                self.slots[index] = {
                    "item": item,
                    "quantity": quantity
                }
                return True

        return False

    def remove_item(self, item, quantity=1):
        if quantity <= 0:
            return False

        for index, slot in enumerate(self.slots):
            if slot is None:
                continue

            if slot["item"] != item:
                continue

            if slot["quantity"] < quantity:
                return False

            slot["quantity"] -= quantity

            if slot["quantity"] == 0:
                self.slots[index] = None

            return True

        return False

    def has_item(self, item):
        return self.get_item_count(item) > 0

    def get_item_count(self, item):
        total = 0

        for slot in self.slots:
            if slot is None:
                continue

            if slot["item"] == item:
                total += slot["quantity"]

        return total

    def get_empty_slot(self):
        for index in range(self.max_slots):
            if self.slots[index] is None:
                return index

        return -1

    def is_full(self):
        return self.get_empty_slot() == -1

    def clear(self):
        self.slots = [None for _ in range(self.max_slots)]

    def debug_print(self):
        print("========== INVENTORY ==========")

        for index, slot in enumerate(self.slots):
            if slot is None:
                print(f"Slot {index + 1}: EMPTY")
            else:
                print(
                    f"Slot {index + 1}: "
                    f"{slot['item']} x{slot['quantity']}"
                )

        print("===============================")
