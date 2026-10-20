import sys
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from world.world import World


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))

    world = World()
    assert len(world.rooms) == 12, f"Expected 12 rooms, got {len(world.rooms)}"

    # Rooms remain separated by space, rather than overlapping wall outlines.
    for index, first in enumerate(world.rooms):
        for second in world.rooms[index + 1:]:
            separated = (
                first["x"] + first["width"] + 2 <= second["x"]
                or second["x"] + second["width"] + 2 <= first["x"]
                or first["y"] + first["height"] + 2 <= second["y"]
                or second["y"] + second["height"] + 2 <= first["y"]
            )
            assert separated, f"Rooms overlap or lack a 2-tile gap: {first}, {second}"

    # Each chamber needs an actual 2-tile opening on at least one wall.
    for room in world.rooms:
        left = room["x"]
        top = room["y"]
        right = left + room["width"] - 1
        bottom = top + room["height"] - 1
        has_double_door = False

        for column in range(left + 1, right):
            if (
                world.tiles[top][column] == World.FLOOR
                and world.tiles[top][column + 1] == World.FLOOR
            ):
                has_double_door = True
            if (
                world.tiles[bottom][column] == World.FLOOR
                and world.tiles[bottom][column + 1] == World.FLOOR
            ):
                has_double_door = True

        for row in range(top + 1, bottom):
            if (
                world.tiles[row][left] == World.FLOOR
                and world.tiles[row + 1][left] == World.FLOOR
            ):
                has_double_door = True
            if (
                world.tiles[row][right] == World.FLOOR
                and world.tiles[row + 1][right] == World.FLOOR
            ):
                has_double_door = True

        assert has_double_door, f"Room has no 2-tile doorway: {room}"

    # Every room center is reachable using floor tiles only.
    start = (
        world.rooms[0]["center_x"],
        world.rooms[0]["center_y"]
    )
    for room in world.rooms:
        goal = (room["center_x"], room["center_y"])
        path = world.find_path(start, goal)
        assert path, f"No path from {start} to {goal}"
        assert path[0] == start and path[-1] == goal
        for column, row in path:
            assert world.tiles[row][column] == World.FLOOR
        for current, following in zip(path, path[1:]):
            distance = (
                abs(current[0] - following[0])
                + abs(current[1] - following[1])
            )
            assert distance == 1, "Path contains a non-adjacent step"

    # Spawn and collision semantics still agree with the three-state map.
    spawn_x, spawn_y = world.get_center_spawn_position()
    spawn_rect = pygame.Rect(spawn_x, spawn_y, 40, 40)
    assert not world.collides_with_wall(spawn_rect)

    void_tile = next(
        (column, row)
        for row in range(1, world.rows - 1)
        for column in range(1, world.columns - 1)
        if world.tiles[row][column] == World.VOID
    )
    void_rect = pygame.Rect(
        void_tile[0] * world.TILE_SIZE,
        void_tile[1] * world.TILE_SIZE,
        world.TILE_SIZE,
        world.TILE_SIZE
    )
    assert world.collides_with_wall(void_rect), "Uncarved void must be solid"

    # Void cells touching the walkable map should receive a visible masonry
    # edge instead of exposing rubble along room/corridor boundaries.
    boundary_void_tiles = [
        (column, row)
        for row in range(1, world.rows - 1)
        for column in range(1, world.columns - 1)
        if world.tiles[row][column] == World.VOID
        and world.is_void_boundary(column, row)
    ]
    assert boundary_void_tiles, "Expected exposed floor/void boundaries"

    for column, row in boundary_void_tiles:
        assert world.tiles[row][column] == World.VOID
        assert world.collides_with_wall(
            pygame.Rect(
                column * world.TILE_SIZE,
                row * world.TILE_SIZE,
                world.TILE_SIZE,
                world.TILE_SIZE
            )
        ), "Visual edge masking must not make VOID walkable"

    pygame.quit()
    print(
        "Dungeon generation checks passed: "
        "12 separated rooms, double-width doorways, connected paths, "
        "safe spawn, and solid void."
    )


if __name__ == "__main__":
    main()
