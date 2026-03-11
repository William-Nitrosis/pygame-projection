from __future__ import annotations

from typing import TYPE_CHECKING

from sprite_object import AnimatedSprite

if TYPE_CHECKING:
    from main import Game


class ObjectHandler:
    """Owns world objects (sprites) and updates them each frame."""

    def __init__(self, game: Game) -> None:
        self.game = game

        self.sprite_list: list[AnimatedSprite] = []

        self.static_sprite_path = "resources/sprites/static_sprites/"
        self.anim_sprite_path = "resources/sprites/animated_sprites/"

        # -----------------------------------------------------------------
        # Sprite placement (decor)
        # -----------------------------------------------------------------
        self.add_sprite(AnimatedSprite(game, pos=(2.5, 2.5)))
        self.add_sprite(AnimatedSprite(game, pos=(2.5, 3.5), path=self.anim_sprite_path + "red_light/0.png"))

    def check_win(self) -> None:
        """stub"""
        pass

    def update(self) -> None:
        for sprite in self.sprite_list:
            sprite.update()

        self.check_win()

    def add_sprite(self, sprite: AnimatedSprite) -> None:
        self.sprite_list.append(sprite)
