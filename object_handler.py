from __future__ import annotations

from typing import TYPE_CHECKING
import math

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

        # Goal object
        self.add_sprite(
            AnimatedSprite(
                game,
                pos=(2.5, 2.5),
                path=self.anim_sprite_path + "green_light/0.png",
                is_goal=True,
                trigger_radius=0.65,
            )
        )

        # Decor
        self.add_sprite(
            AnimatedSprite(
                game,
                pos=(2.5, 3.5),
                path=self.anim_sprite_path + "red_light/0.png",
            )
        )

    def check_win(self) -> None:
        """Trigger level completion when the player reaches a goal sprite."""
        if self.game.level_complete:
            return

        px, py = self.game.player.pos

        for sprite in self.sprite_list:
            if not sprite.is_goal:
                continue

            dist = math.hypot(sprite.x - px, sprite.y - py)
            if dist <= sprite.trigger_radius:
                self.game.start_level_complete()
                return

    def update(self) -> None:
        for sprite in self.sprite_list:
            sprite.update()

        self.check_win()

    def add_sprite(self, sprite: AnimatedSprite) -> None:
        self.sprite_list.append(sprite)
