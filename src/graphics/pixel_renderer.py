
import pygame


class PixelRenderer:
    """
    Reusable drawing helpers for the Dungeon RPG.

    Keeps pixel artwork crisp and provides shared drawing utilities.
    This module does not modify world tiles, collision, or game logic.
    """

    def __init__(self):
        self._texture_cache = {}

    @staticmethod
    def create_surface(size, transparent=True):
        """Create a surface suitable for pixel-art textures."""
        flags = pygame.SRCALPHA if transparent else 0
        return pygame.Surface(size, flags)

    @staticmethod
    def scale_pixel_art(surface, size):
        """Scale artwork without smoothing its pixel edges."""
        return pygame.transform.scale(surface, size)

    @staticmethod
    def draw_pixel_rect(surface, color, rect):
        """Draw a rectangle aligned to whole pixels."""
        rect = pygame.Rect(rect)
        pygame.draw.rect(surface, color, rect)

    @staticmethod
    def draw_pixel_border(surface, color, rect, thickness=1):
        """Draw a crisp rectangular border."""
        rect = pygame.Rect(rect)
        pygame.draw.rect(
            surface,
            color,
            rect,
            width=max(1, int(thickness)),
        )

    def get_cached_texture(self, key):
        """Return a previously cached texture, or None."""
        return self._texture_cache.get(key)

    def cache_texture(self, key, surface):
        """Store a completed texture so it can be reused."""
        self._texture_cache[key] = surface
        return surface

    def clear_cache(self):
        """Clear cached textures when they need to be rebuilt."""
        self._texture_cache.clear()
