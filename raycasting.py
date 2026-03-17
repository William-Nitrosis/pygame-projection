from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

import math
import pygame as pg

from settings import (
    DELTA_ANGLE,
    HALF_FOV,
    HALF_HEIGHT,
    HALF_TEXTURE_SIZE,
    HEIGHT,
    MAX_DEPTH,
    NUM_RAYS,
    SCALE,
    SCREEN_DIST,
    TEXTURE_SIZE,
)

if TYPE_CHECKING:
    from main import Game


EPS = 1e-6


class RayCasting:
    """Performs wall raycasts and prepares renderable wall columns."""

    def __init__(self, game: Game) -> None:
        self.game = game
        self.ray_casting_result: List[Tuple[float, int, int, float, bool]] = []
        self.objects_to_render: List[Tuple[float, pg.Surface, Tuple[int, int]]] = []
        self.textures = self.game.object_renderer.wall_textures

    def get_objects_to_render(self) -> None:
        """Turn raycast results into scaled wall column surfaces."""
        self.objects_to_render = []

        for ray, (depth, proj_height, texture, offset, is_vertical) in enumerate(
            self.ray_casting_result
        ):
            tex = self.textures[texture]

            if proj_height < HEIGHT:
                wall_column = tex.subsurface(
                    offset * (TEXTURE_SIZE - SCALE), 0, SCALE, TEXTURE_SIZE
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, proj_height))
                wall_pos = (ray * SCALE, HALF_HEIGHT - proj_height // 2)
            else:
                texture_height = TEXTURE_SIZE * HEIGHT / proj_height
                wall_column = tex.subsurface(
                    offset * (TEXTURE_SIZE - SCALE),
                    HALF_TEXTURE_SIZE - texture_height // 2,
                    SCALE,
                    texture_height,
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, HEIGHT))
                wall_pos = (ray * SCALE, 0)

            # fake contrast - darken one wall orientation
            if is_vertical:
                distance_darkness = max(0.35, 1.0 / (1.0 + depth * 0.1))
                shade_value = int(255 * distance_darkness)

                shade = pg.Surface(wall_column.get_size(), pg.SRCALPHA)
                shade.fill((shade_value, shade_value, shade_value, 255))
                wall_column.blit(shade, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

            self.objects_to_render.append((depth, wall_column, wall_pos))

    def ray_cast(self) -> None:
        """Cast rays and record wall hit depths + texture offsets."""
        self.ray_casting_result = []

        texture_vert = 1
        texture_hor = 1

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.game.player.angle - HALF_FOV + 0.0001

        for _ in range(NUM_RAYS):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            # avoid division by ~0
            if abs(sin_a) < EPS:
                sin_a = EPS if sin_a >= 0 else -EPS
            if abs(cos_a) < EPS:
                cos_a = EPS if cos_a >= 0 else -EPS

            # -----------------------------------------------------------------
            # horizontals
            # -----------------------------------------------------------------
            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a

            delta_depth = dy / sin_a
            dx = delta_depth * cos_a

            for _i in range(MAX_DEPTH):
                tile_hor = int(x_hor), int(y_hor)
                if tile_hor in self.game.map.world_map:
                    texture_hor = self.game.map.world_map[tile_hor]
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta_depth

            # -----------------------------------------------------------------
            # verticals
            # -----------------------------------------------------------------
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a

            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            for _i in range(MAX_DEPTH):
                tile_vert = int(x_vert), int(y_vert)
                if tile_vert in self.game.map.world_map:
                    texture_vert = self.game.map.world_map[tile_vert]
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth

            # depth + texture offset
            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1 - y_vert)
                is_vertical = True
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = (1 - x_hor) if sin_a > 0 else x_hor
                is_vertical = False

            # remove fishbowl effect
            depth *= math.cos(self.game.player.angle - ray_angle)

            # projection
            proj_height = int(SCREEN_DIST / (depth + 0.0001))

            self.ray_casting_result.append(
                (depth, proj_height, texture, offset, is_vertical)
            )
            ray_angle += DELTA_ANGLE

    def update(self) -> None:
        self.ray_cast()
        self.get_objects_to_render()
