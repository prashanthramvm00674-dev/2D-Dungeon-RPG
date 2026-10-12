import sys
from pathlib import Path

import pygame

# Add the project's src directory to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from world.world import World
from core.camera import Camera


def main():
    pygame.init()

    # Use current resolution (1280x720)
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Stage 2: Wall Textures Preview")

    world = World()
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Position camera to show both floor and wall textures
    # Focus on the central corridor area
    camera.update(
        pygame.Rect(400, 280, 40, 40),
        world.get_width(),
        world.get_height()
    )

    # Render single frame
    screen.fill((20, 20, 25))
    world.render(screen, camera)

    # Save screenshot
    screenshot_path = PROJECT_ROOT / "tests" / "stage2_preview.png"
    pygame.image.save(screen, str(screenshot_path))

    print(f"Stage 2 preview saved to: {screenshot_path}")

    pygame.quit()


if __name__ == "__main__":
    main()
