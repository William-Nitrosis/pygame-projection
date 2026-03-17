from __future__ import annotations

from typing import TYPE_CHECKING, Deque, Tuple

import math
import os
from collections import deque

import pygame as pg

from settings import DELTA_ANGLE, HALF_HEIGHT, HALF_NUM_RAYS, SCALE, SCREEN_DIST, WIDTH

if TYPE_CHECKING:
    from main import Game


class SpriteObject:
    """A single billboard sprite in the world."""

    def __init__(
        self,
        game: Game,
        path: str = "resources/sprites/static_sprites/candlebra.png",
        pos: Tuple[float, float] = (10.5, 3.5),
        scale: float = 0.7,
        shift: float = 0.27,
    ) -> None:
        self.game = game
        self.player = game.player

        self.x, self.y = pos
        self.image = pg.image.load(path).convert_alpha()

        self.image_width = self.image.get_width()
        self.image_half_width = self.image_width // 2
        self.image_ratio = self.image_width / self.image.get_height()

        self.dx = 0.0
        self.dy = 0.0
        self.theta = 0.0
        self.screen_x = 0.0
        self.dist = 1.0
        self.norm_dist = 1.0

        self.sprite_half_width = 0
        self.sprite_scale = float(scale)
        self.sprite_height_shift = float(shift)

        # gameplay flags
        self.is_goal = False
        self.trigger_radius = 0.6

    def get_sprite_projection(self) -> None:
        proj = SCREEN_DIST / self.norm_dist * self.sprite_scale
        proj_width = int(proj * self.image_ratio)
        proj_height = int(proj)

        if proj_width < 1 or proj_height < 1:
            return

        image = pg.transform.scale(self.image, (proj_width, proj_height))
        self.sprite_half_width = proj_width // 2

        height_shift = int(proj_height * self.sprite_height_shift)
        pos = (
            int(self.screen_x - self.sprite_half_width),
            int(HALF_HEIGHT - proj_height // 2 + height_shift),
        )

        self.game.raycasting.objects_to_render.append((self.norm_dist, image, pos))

    def get_sprite(self) -> None:
        dx = self.x - self.player.x
        dy = self.y - self.player.y
        self.dx, self.dy = dx, dy

        self.theta = math.atan2(dy, dx)

        delta = self.theta - self.player.angle
        if (dx > 0 and self.player.angle > math.pi) or (dx < 0 and dy < 0):
            delta += math.tau

        delta_rays = delta / DELTA_ANGLE
        self.screen_x = (HALF_NUM_RAYS + delta_rays) * SCALE

        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(delta)

        if (
            -self.image_half_width < self.screen_x < (WIDTH + self.image_half_width)
            and self.norm_dist > 0.5
        ):
            self.get_sprite_projection()

    def update(self) -> None:
        self.get_sprite()


class AnimatedSprite(SpriteObject):
    """A sprite that cycles through images loaded from a directory."""

    def __init__(
        self,
        game: Game,
        path: str = "resources/sprites/animated_sprites/green_light/0.png",
        pos: Tuple[float, float] = (11.5, 3.5),
        scale: float = 0.8,
        shift: float = 0.16,
        animation_time: int = 120,
        is_goal: bool = False,
        trigger_radius: float = 0.6,
    ) -> None:
        super().__init__(game, path, pos, scale, shift)

        self.animation_time = int(animation_time)
        self.path = path.rsplit("/", 1)[0]
        self.images: Deque[pg.Surface] = self.get_images(self.path)

        self.animation_time_prev = pg.time.get_ticks()
        self.animation_trigger = False

        self.is_goal = is_goal
        self.trigger_radius = trigger_radius

    def update(self) -> None:
        super().update()
        self.check_animation_time()
        self.animate(self.images)

    def animate(self, images: Deque[pg.Surface]) -> None:
        if self.animation_trigger and images:
            images.rotate(-1)
            self.image = images[0]

    def check_animation_time(self) -> None:
        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    def get_images(self, path: str) -> Deque[pg.Surface]:
        images: Deque[pg.Surface] = deque()
        for file_name in sorted(os.listdir(path)):
            full = os.path.join(path, file_name)
            if os.path.isfile(full):
                img = pg.image.load(full).convert_alpha()
                images.append(img)
        return images