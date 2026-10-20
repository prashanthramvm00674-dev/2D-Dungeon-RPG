import sys
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from entities.item import HEALTH_POTION
from entities.loot import Loot


class IdentityCamera:
    def apply(self, rect):
        return rect.copy()


def main():
    pygame.init()
    canvas = pygame.Surface((96, 96))
    canvas.fill((18, 23, 29))

    loot = Loot(36, 36, HEALTH_POTION)
    loot.render(canvas, IdentityCamera())

    # The pickup must visibly contain red potion glass/liquid, not the old
    # uniform green rectangle used as a temporary placeholder.
    red_pixels = 0
    green_placeholder_pixels = 0
    for y in range(18, 78):
        for x in range(18, 78):
            red, green, blue, _alpha = canvas.get_at((x, y))
            if red > 140 and green < 115 and blue < 125:
                red_pixels += 1
            if (red, green, blue) == (80, 220, 100):
                green_placeholder_pixels += 1

    assert red_pixels >= 12, f"Potion silhouette is missing (red pixels: {red_pixels})"
    assert green_placeholder_pixels == 0, "Old green debug loot square remains"

    pygame.quit()
    print("Loot rendering passed: dropped health potion shows a red bottle icon.")


if __name__ == "__main__":
    main()
