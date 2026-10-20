import pygame


class LightingSystem:
    """
    Lightweight, cached 2D lighting for the dungeon.

    Draw the normal world and entities first, then call render() before the
    HUD. A cool ambient overlay darkens the scene; cached radial overlays add
    warm torchlight and a subtle visibility light around the player.
    """

    AMBIENT_COLOR = (4, 8, 15, 142)

    # Two cached warm layers create a broad torch halo and a brighter core.
    TORCH_GLOW_RADIUS = 300
    TORCH_GLOW_COLOR = (255, 120, 42)
    TORCH_GLOW_STRENGTH = 34
    TORCH_RADIUS = 220
    TORCH_COLOR = (255, 165, 82)
    TORCH_STRENGTH = 138

    # A restrained cool halo keeps the player readable without flattening
    # the warm/cool contrast that defines the target image.
    PLAYER_GLOW_RADIUS = 205
    PLAYER_GLOW_COLOR = (85, 130, 205)
    PLAYER_GLOW_STRENGTH = 22
    PLAYER_RADIUS = 140
    PLAYER_COLOR = (120, 165, 230)
    PLAYER_STRENGTH = 78

    def __init__(self):
        self._light_cache = {}
        self._ambient_surface = None
        self._ambient_size = None

    def _get_light_texture(self, radius, color, strength):
        """Build and cache a radial alpha-gradient surface."""
        key = (int(radius), tuple(color), int(strength))
        cached = self._light_cache.get(key)

        if cached is not None:
            return cached

        radius = max(1, int(radius))
        diameter = radius * 2
        light = pygame.Surface(
            (diameter, diameter),
            pygame.SRCALPHA
        )
        center = (radius, radius)

        # Larger faint circles are drawn first; inner circles become brighter.
        # The texture is cached, so these circles are not redrawn every frame.
        for circle_radius in range(radius, 0, -3):
            falloff = 1.0 - (circle_radius / radius)
            alpha = int(
                4 + (max(0, strength - 4) * (falloff ** 1.65))
            )
            pygame.draw.circle(
                light,
                (color[0], color[1], color[2], alpha),
                center,
                circle_radius
            )

        self._light_cache[key] = light
        return light

    def _get_ambient_surface(self, size):
        """
        Reuse a constant-alpha ambient shade.

        A regular RGB surface with Surface.set_alpha uses SDL's uniform-alpha
        blit path. A per-pixel SRCALPHA surface covering the entire fullscreen
        viewport was needlessly expensive on every rendered frame.
        """
        if self._ambient_surface is None or self._ambient_size != size:
            ambient = pygame.Surface(size)
            ambient.fill(self.AMBIENT_COLOR[:3])
            ambient.set_alpha(self.AMBIENT_COLOR[3])
            self._ambient_surface = ambient
            self._ambient_size = size

        return self._ambient_surface

    @staticmethod
    def _light_is_visible(screen_rect, position, radius):
        light_rect = pygame.Rect(
            position[0] - radius,
            position[1] - radius,
            radius * 2,
            radius * 2
        )
        return light_rect.colliderect(screen_rect)

    def _draw_light(self, screen, camera, world_position, radius, color, strength):
        world_point = pygame.Rect(
            int(world_position[0]),
            int(world_position[1]),
            1,
            1
        )
        screen_point = camera.apply(world_point).topleft
        viewport = screen.get_rect()

        if not self._light_is_visible(viewport, screen_point, radius):
            return

        texture = self._get_light_texture(radius, color, strength)
        screen.blit(
            texture,
            (screen_point[0] - radius, screen_point[1] - radius)
        )

    def render(self, screen, torches, player, camera):
        """
            Apply ambient darkness and lights in screen space.

        Torch entries use world-pixel center coordinates: {"x": int, "y": int}.
        Call this before the HUD so interface elements stay crisp and readable.
        """
        viewport_size = screen.get_size()
        screen.blit(
            self._get_ambient_surface(viewport_size),
            (0, 0)
        )
        # Render the broad low-energy glow before the smaller light core.
        # Ordering these layers creates a soft pool rather than a flat orange
        # circle, while all textures remain cached between frames.
        for torch in torches:
            position = (torch["x"], torch["y"])
            self._draw_light(
                screen,
                camera,
                position,
                self.TORCH_GLOW_RADIUS,
                self.TORCH_GLOW_COLOR,
                self.TORCH_GLOW_STRENGTH
            )
            self._draw_light(
                screen,
                camera,
                position,
                self.TORCH_RADIUS,
                self.TORCH_COLOR,
                self.TORCH_STRENGTH
            )

        # Add a low-power cool halo followed by the brighter player visibility
        # light, preserving contrast against torchlit stone.
        self._draw_light(
            screen,
            camera,
            player.rect.center,
            self.PLAYER_GLOW_RADIUS,
            self.PLAYER_GLOW_COLOR,
            self.PLAYER_GLOW_STRENGTH
        )
        self._draw_light(
            screen,
            camera,
            player.rect.center,
            self.PLAYER_RADIUS,
            self.PLAYER_COLOR,
            self.PLAYER_STRENGTH
        )
