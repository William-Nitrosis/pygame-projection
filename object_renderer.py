from __future__ import annotations

import math
from typing import TYPE_CHECKING, Dict

import pygame as pg

from settings import (
    FLOOR_COLOR,
    FLOOR_RENDER_SCALE,
    FLOOR_TEX_SCALE,
    HALF_FOV,
    HALF_HEIGHT,
    HEIGHT,
    RES,
    SCREEN_DIST,
    TEXTURE_SIZE,
    WIDTH,
)

if TYPE_CHECKING:
    from main import Game


class ObjectRenderer:
    """Draws the scene using the raycaster results."""

    def __init__(self, game: Game) -> None:
        self.game = game
        self.screen = game.screen

        self.wall_textures = self.load_wall_textures()

        self.sky_image = self.get_texture(
            "resources/textures/sky3.png", (WIDTH, HALF_HEIGHT)
        )
        self.sky_offset = 0.0

        self.win_image = self.get_texture("resources/textures/win.png", RES)

        self.floor_texture = self.get_texture("resources/textures/floor.png")
        self.floor_buffer = pg.Surface(
            (WIDTH // FLOOR_RENDER_SCALE, HALF_HEIGHT // FLOOR_RENDER_SCALE)
        ).convert()

    def draw(self) -> None:
        self.draw_background()
        self.render_game_objects()

    def win(self) -> None:
        self.screen.blit(self.win_image, (0, 0))

    def draw_background(self) -> None:
        # scroll sky based on player mouse delta (rel)
        self.sky_offset = (self.sky_offset + 4.0 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))

        # floor
        # pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))
        self.draw_textured_floor_fast()

    def render_game_objects(self) -> None:
        objects = sorted(
            self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True
        )
        for _depth, image, pos in objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path: str, res=(TEXTURE_SIZE, TEXTURE_SIZE)) -> pg.Surface:
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self) -> Dict[int, pg.Surface]:
        return {
            1: self.get_texture("resources/textures/1.png"),
            2: self.get_texture("resources/textures/2.png"),
            3: self.get_texture("resources/textures/3.png"),
            4: self.get_texture("resources/textures/4.png"),
            5: self.get_texture("resources/textures/5.png"),
            6: self.get_texture("resources/textures/6.png"),
            7: self.get_texture("resources/textures/7.png"),
            8: self.get_texture("resources/textures/8.png"),
            9: self.get_texture("resources/textures/9.png"),
        }

    def draw_textured_floor_fast(self) -> None:
        """Draw a textured floor using a low-resolution perspective buffer."""
        player = self.game.player
        tex = self.floor_texture
        tex_w, tex_h = tex.get_size()

        buf = self.floor_buffer
        buf_w, buf_h = buf.get_size()

        angle_left = player.angle - HALF_FOV
        angle_right = player.angle + HALF_FOV

        left_dx = math.cos(angle_left)
        left_dy = math.sin(angle_left)
        right_dx = math.cos(angle_right)
        right_dy = math.sin(angle_right)

        camera_height = 0.5

        buf.lock()

        for y in range(buf_h):
            # row in actual screen space, bottom half only
            screen_y = HALF_HEIGHT + y * FLOOR_RENDER_SCALE
            p = screen_y - HALF_HEIGHT

            if p <= 0:
                continue

            # this is the important fix
            row_dist = (camera_height * SCREEN_DIST) / p

            start_x = player.x + row_dist * left_dx
            start_y = player.y + row_dist * left_dy
            end_x = player.x + row_dist * right_dx
            end_y = player.y + row_dist * right_dy

            step_x = (end_x - start_x) / buf_w
            step_y = (end_y - start_y) / buf_w

            world_x = start_x
            world_y = start_y

            for x in range(0, buf_w, 2):
                tx = int(world_x * tex_w * FLOOR_TEX_SCALE) % tex_w
                ty = int(world_y * tex_h * FLOOR_TEX_SCALE) % tex_h

                color = tex.get_at((tx, ty))

                shade = max(0.35, min(1.0, 6.0 / (row_dist + 0.0001)))
                r = int(color.r * shade)
                g = int(color.g * shade)
                b = int(color.b * shade)

                buf.set_at((x, y), (r, g, b))
                if x + 1 < buf_w:
                    buf.set_at((x + 1, y), (r, g, b))

                world_x += step_x * 2
                world_y += step_y * 2

        buf.unlock()

        scaled = pg.transform.scale(buf, (WIDTH, HALF_HEIGHT))
        self.screen.blit(scaled, (0, HALF_HEIGHT))
