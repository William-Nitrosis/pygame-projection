"""weapon.py

First-person weapon sprite and firing animation.

Currently implements a shotgun-like weapon:
- Plays an animation sequence while reloading.
- Sets `player.shot` to False once the animation advances.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Deque

from collections import deque

import pygame as pg

from settings import HALF_WIDTH, HEIGHT
from sprite_object import AnimatedSprite

if TYPE_CHECKING:
    from main import Game


class Weapon(AnimatedSprite):
    """Animated weapon view-model."""

    def __init__(
        self,
        game: Game,
        path: str = "resources/sprites/weapon/shotgun/0.png",
        scale: float = 0.4,
        animation_time: int = 90,
    ) -> None:
        super().__init__(
            game=game, path=path, scale=scale, animation_time=animation_time
        )

        # Pre-scale frames once (avoid per-frame scaling).
        scaled: Deque[pg.Surface] = deque()
        for img in self.images:
            w = int(img.get_width() * scale)
            h = int(img.get_height() * scale)
            scaled.append(pg.transform.smoothscale(img, (w, h)))
        self.images = scaled
        self.image = self.images[0]

        self.weapon_pos = (
            HALF_WIDTH - self.images[0].get_width() // 2,
            HEIGHT - self.images[0].get_height(),
        )

        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0

        self.damage = 50

    def animate_shot(self) -> None:
        """Advance animation while reloading."""
        if not self.reloading:
            return

        # once the weapon starts animating, consume the shot so it can't multi-hit
        self.game.player.shot = False

        if self.animation_trigger:
            self.images.rotate(-1)
            self.image = self.images[0]
            self.frame_counter += 1

            if self.frame_counter == self.num_images:
                self.reloading = False
                self.frame_counter = 0

    def draw(self) -> None:
        self.game.screen.blit(self.images[0], self.weapon_pos)

    def update(self) -> None:
        self.check_animation_time()
        self.animate_shot()
