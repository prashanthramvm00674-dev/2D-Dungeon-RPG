import math

import pygame


class ScenePostProcessor:
    """Lightweight, real-time finishing pass for the rendered dungeon scene.

    The pass is deliberately non-destructive: it adjusts only the current
    display surface, does not rescale or blur pixel art, and runs before the
    HUD so interface text and borders remain sharp and unchanged.

    The tone lift recovers a little shadow detail without washing out torch
    highlights. A cached low-resolution vignette gently directs attention
    toward the playable center without expensive per-frame pixel processing.
    """

    # A very transparent cool highlight overlay gives dark areas a gentle
    # shadow lift while keeping vivid amber torch lights recognizable.
    TONE_TINT = (135, 145, 160)
    TONE_ALPHA = 18

    # Subtle maximum opacity at the extreme corners; the middle stays clear.
    VIGNETTE_MAX_ALPHA = 20
    VIGNETTE_START_RADIUS = 0.58

    def __init__(self):
        self._vignette_cache = {}
        self._grade_surface_cache = {}

    def _build_vignette(self, size):
        """Build a soft elliptical vignette once for a given display size."""
        width, height = size
        if width <= 0 or height <= 0:
            raise ValueError("Post-processing needs a positive display size.")

        cache_key = (width, height)
        cached = self._vignette_cache.get(cache_key)
        if cached is not None:
            return cached

        # Build at quarter resolution and scale once. This keeps setup light
        # even if the user changes between windowed and fullscreen modes.
        low_width = max(48, min(width, width // 4))
        low_height = max(36, min(height, height // 4))
        vignette = pygame.Surface(
            (low_width, low_height),
            pygame.SRCALPHA,
            32
        )
        pixels = pygame.PixelArray(vignette)
        max_radius = math.sqrt(2.0)
        span = max(0.001, max_radius - self.VIGNETTE_START_RADIUS)

        for y in range(low_height):
            ny = ((y / max(1, low_height - 1)) - 0.5) * 2.0
            for x in range(low_width):
                nx = ((x / max(1, low_width - 1)) - 0.5) * 2.0
                radius = math.sqrt(nx * nx + ny * ny)
                amount = max(
                    0.0,
                    min(1.0, (radius - self.VIGNETTE_START_RADIUS) / span)
                )
                # Smoothstep avoids a visible ring or abrupt boundary.
                amount = amount * amount * (3.0 - 2.0 * amount)
                alpha = int(round(self.VIGNETTE_MAX_ALPHA * amount))
                pixels[x, y] = (0, 0, 0, alpha)

        del pixels
        vignette = pygame.transform.smoothscale(vignette, size)
        vignette.set_alpha(None)
        self._vignette_cache[cache_key] = vignette
        return vignette

    def _get_grade_surface(self, size):
        """Cache a translucent color-grade surface for the current viewport."""
        cached = self._grade_surface_cache.get(size)
        if cached is not None:
            return cached

        grade = pygame.Surface(size, pygame.SRCALPHA, 32)
        grade.fill((*self.TONE_TINT, self.TONE_ALPHA))
        self._grade_surface_cache[size] = grade
        return grade

    def apply(self, screen):
        """Apply a gentle shadow-recovery grade and a cached soft vignette."""
        # Both are cached full-screen blits: no per-frame allocation, rescaling,
        # NumPy dependency, or Python-level pixel loop.
        screen.blit(
            self._get_grade_surface(screen.get_size()),
            (0, 0)
        )
        screen.blit(
            self._build_vignette(screen.get_size()),
            (0, 0)
        )
