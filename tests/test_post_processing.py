import sys
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from graphics.post_processing import ScenePostProcessor


def main():
    pygame.init()
    processor = ScenePostProcessor()

    # Shadow detail lifts slightly without flattening the dark-fantasy palette.
    scene = pygame.Surface((160, 90))
    scene.fill((25, 30, 40))
    processor.apply(scene)
    center = scene.get_at((80, 45))
    corner = scene.get_at((0, 0))
    assert center.r > 25 and center.g > 30 and center.b > 40
    assert corner.r <= center.r
    assert corner.g <= center.g
    assert corner.b <= center.b

    # Highlights retain their brightness and warm character after the grade.
    highlights = pygame.Surface((160, 90))
    highlights.fill((245, 140, 55))
    processor.apply(highlights)
    warm_highlight = highlights.get_at((80, 45))
    assert warm_highlight.r >= 240, (
        f"Torch highlight was crushed: {warm_highlight}"
    )
    assert warm_highlight.r > warm_highlight.g > warm_highlight.b

    # Vignette is reused at a stable size and rebuilt safely after resizing.
    first = processor._build_vignette((160, 90))
    second = processor._build_vignette((160, 90))
    resized = processor._build_vignette((320, 180))
    assert first is second
    assert resized.get_size() == (320, 180)

    pygame.quit()
    print(
        "Post-processing checks passed: lifted shadows, retained warm "
        "highlights, subtle vignette, and cached resize-safe surfaces."
    )


if __name__ == "__main__":
    main()
