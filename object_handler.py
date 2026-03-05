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
        self.add_sprite(AnimatedSprite(game))
        self.add_sprite(AnimatedSprite(game, pos=(1.5, 1.5)))
        self.add_sprite(AnimatedSprite(game, pos=(1.5, 7.5)))
        self.add_sprite(AnimatedSprite(game, pos=(5.5, 3.25)))
        self.add_sprite(AnimatedSprite(game, pos=(5.5, 4.75)))
        self.add_sprite(AnimatedSprite(game, pos=(7.5, 2.5)))
        self.add_sprite(AnimatedSprite(game, pos=(7.5, 5.5)))
        self.add_sprite(AnimatedSprite(game, pos=(14.5, 1.5)))
        self.add_sprite(AnimatedSprite(game, pos=(14.5, 4.5)))

        for pos in [
            (14.5, 5.5),
            (14.5, 7.5),
            (12.5, 7.5),
            (9.5, 7.5),
            (14.5, 12.5),
            (9.5, 20.5),
            (10.5, 20.5),
            (3.5, 14.5),
            (3.5, 18.5),
        ]:
            self.add_sprite(
                AnimatedSprite(
                    game, path=self.anim_sprite_path + "red_light/0.png", pos=pos
                )
            )

        self.add_sprite(AnimatedSprite(game, pos=(14.5, 24.5)))
        self.add_sprite(AnimatedSprite(game, pos=(14.5, 30.5)))
        self.add_sprite(AnimatedSprite(game, pos=(1.5, 30.5)))
        self.add_sprite(AnimatedSprite(game, pos=(1.5, 24.5)))

    def check_win(self) -> None:
        """stub"""
        pass

    def update(self) -> None:
        for sprite in self.sprite_list:
            sprite.update()

        self.check_win()

    def add_sprite(self, sprite: AnimatedSprite) -> None:
        self.sprite_list.append(sprite)
