from __future__ import annotations

from typing import TYPE_CHECKING
import math

from sprite_object import AnimatedSprite, SpriteObject

if TYPE_CHECKING:
    from main import Game


class ObjectHandler:
    """Owns world objects, loads them from level metadata, and updates them."""

    def __init__(self, game: Game) -> None:
        self.game = game

        self.sprite_list: list[SpriteObject] = []

        self.static_sprite_path = "resources/sprites/static_sprites/"
        self.anim_sprite_path = "resources/sprites/animated_sprites/"

        self.load_sprites_from_map()

    def load_sprites_from_map(self) -> None:
        """Build sprite instances from map JSON metadata."""
        self.sprite_list.clear()

        sprites_data = self.game.map.meta.get("sprites", [])
        if not isinstance(sprites_data, list):
            return

        for item in sprites_data:
            if not isinstance(item, dict):
                continue

            kind = str(item.get("kind", "animated")).lower()
            sprite_name = str(item.get("sprite", "green_light"))
            pos_data = item.get("pos", [1.5, 1.5])

            if not isinstance(pos_data, (list, tuple)) or len(pos_data) != 2:
                continue

            pos = (float(pos_data[0]), float(pos_data[1]))
            scale = float(item.get("scale", 0.8 if kind == "animated" else 0.7))
            shift = float(item.get("shift", 0.16 if kind == "animated" else 0.27))
            is_goal = bool(item.get("goal", False))
            trigger_radius = float(item.get("trigger_radius", 0.6))

            if kind == "static":
                path = self._resolve_static_path(sprite_name)
                sprite = SpriteObject(
                    self.game,
                    path=path,
                    pos=pos,
                    scale=scale,
                    shift=shift,
                    is_goal=is_goal,
                    trigger_radius=trigger_radius,
                )
            else:
                animation_time = int(item.get("animation_time", 120))
                path = self._resolve_animated_path(sprite_name)
                sprite = AnimatedSprite(
                    self.game,
                    path=path,
                    pos=pos,
                    scale=scale,
                    shift=shift,
                    animation_time=animation_time,
                    is_goal=is_goal,
                    trigger_radius=trigger_radius,
                )

            self.add_sprite(sprite)

    def _resolve_static_path(self, sprite_name: str) -> str:
        """Return a full static sprite file path."""
        if "/" in sprite_name or "\\" in sprite_name:
            return sprite_name
        return self.static_sprite_path + sprite_name

    def _resolve_animated_path(self, sprite_name: str) -> str:
        """Return the first frame path for an animated sprite."""
        if sprite_name.endswith(".png"):
            return sprite_name
        return f"{self.anim_sprite_path}{sprite_name}/0.png"

    def check_win(self) -> None:
        """Trigger level completion when the player touches a goal sprite."""
        if getattr(self.game, "level_complete", False):
            return

        px, py = self.game.player.pos

        for sprite in self.sprite_list:
            if not getattr(sprite, "is_goal", False):
                continue

            dist = math.hypot(sprite.x - px, sprite.y - py)
            if dist <= sprite.trigger_radius:
                self.game.start_level_complete()
                return

    def update(self) -> None:
        for sprite in self.sprite_list:
            sprite.update()

        self.check_win()

    def add_sprite(self, sprite: SpriteObject) -> None:
        self.sprite_list.append(sprite)