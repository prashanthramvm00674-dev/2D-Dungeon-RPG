class Item:

    def __init__(
        self,
        name,
        item_type,
        description="",
        value=0,
        stackable=True
    ):

        self.name = name
        self.item_type = item_type
        self.description = description
        self.value = value
        self.stackable = stackable


# ==================================================
# ITEM DEFINITIONS
# ==================================================

HEALTH_POTION = Item(
    name="Health Potion",
    item_type="consumable",
    description="Restores 25 HP.",
    value=25,
    stackable=True
)


IRON_SWORD = Item(
    name="Iron Sword",
    item_type="weapon",
    description="A basic iron sword.",
    value=10,
    stackable=False
)


SHIELD = Item(
    name="Shield",
    item_type="armor",
    description="A basic defensive shield.",
    value=5,
    stackable=False
)