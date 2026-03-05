from __future__ import annotations

from typing import TYPE_CHECKING, Dict

import pygame as pg

from settings import FLOOR_COLOR, HALF_HEIGHT, HEIGHT, RES, TEXTURE_SIZE, WIDTH

if TYPE_CHECKING:
    from main import Game


class ObjectRenderer:
    """Draws the scene using the raycaster results."""

    def __init__(self, game: Game) -> None:
        self.game = game
        self.screen = game.screen

        self.wall_textures = self.load_wall_textures()

        self.sky_image = self.get_texture(
            "resources/textures/sky.png", (WIDTH, HALF_HEIGHT)
        )
        self.sky_offset = 0.0

        self.win_image = self.get_texture("resources/textures/win.png", RES)

    def draw(self) -> None:
        self.draw_background()
        self.render_game_objects()

    def win(self) -> None:
        self.screen.blit(self.win_image, (0, 0))

    def draw_background(self) -> None:
        # scroll sky based on player mouse delta (rel)
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))

        # floor
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

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
        }
