import math

import pygame


class ScenePostProcessor:
    """Lightweight finishing pass for the rendered dungeon scene.

    A camera-inspired grade gently recovers shadow detail and a soft vignette
    focuses attention toward the playable center. The effect leaves pixel art
    unscaled and unblurred, and is drawn before UI so HUD elements remain crisp.
    The two effects are pre-composed into one cached overlay to minimize the
    cost of full-screen blending on lower-powered hardware.
    """

    TONE_TINT = (135, 145, 160)
    TONE_ALPHA = 18
    VIGNETTE_MAX_ALPHA = 20
    VIGNETTE_START_RADIUS = 0.58

    def __init__(self):
        self._overlay_cache = {}

    def _build_overlay(self, size):
        """Build the combined alpha grade/vignette once per display size."""
        width, height = size
        if width <= 0 or height <= 0:
            raise ValueError("Post-processing needs a positive display size.")

        cached = self._overlay_cache.get(size)
        if cached is not None:
            return cached

        # Vignettes are smooth gradients, so quarter-resolution generation
        # looks clean once scaled and avoids hundreds of thousands of Python
        # pixel operations when the user switches to fullscreen.
        low_width = max(48, min(width, width // 4))
        low_height = max(36, min(height, height // 4))
        overlay = pygame.Surface((low_width, low_height), pygame.SRCALPHA, 32)
        pixels = pygame.PixelArray(overlay)

        max_radius = math.sqrt(2.0)
        span = max(0.001, max_radius - self.VIGNETTE_START_RADIUS)
        grade_fraction = self.TONE_ALPHA / 255.0

        for y in range(low_height):
            ny = ((y / max(1, low_height - 1)) - 0.5) * 2.0
            for x in range(low_width):
                nx = ((x / max(1, low_width - 1)) - 0.5) * 2.0
                radius = math.sqrt(nx * nx + ny * ny)
                amount = max(
                    0.0,
                    min(1.0, (radius - self.VIGNETTE_START_RADIUS) / span)
                )
                # Smoothstep creates a gradual edge instead of a visible ring.
                amount = amount * amount * (3.0 - 2.0 * amount)
                vignette_fraction = (
                    self.VIGNETTE_MAX_ALPHA * amount / 255.0
                )

                # Compose the translucent cool grade followed by black
                # vignette into one equivalent RGBA pixel:
                # alpha = vignette + grade * (1 - vignette).
                total_alpha = (
                    vignette_fraction
                    + grade_fraction * (1.0 - vignette_fraction)
                )
                alpha_byte = int(round(total_alpha * 255))
                grade_contribution = (
                    grade_fraction * (1.0 - vignette_fraction)
                )
                color_ratio = (
                    grade_contribution / total_alpha
                    if total_alpha > 0
                    else 0.0
                )
                red, green, blue = (
                    int(round(channel * color_ratio))
                    for channel in self.TONE_TINT
                )
                pixels[x, y] = (red, green, blue, alpha_byte)

        del pixels
        overlay = pygame.transform.smoothscale(overlay, size)
        self._overlay_cache[size] = overlay
        return overlay

    def apply(self, screen):
        """Apply the cached finishing overlay with one full-screen blit."""
        screen.blit(self._build_overlay(screen.get_size()), (0, 0))
