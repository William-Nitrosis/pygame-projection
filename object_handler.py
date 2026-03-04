"""object_handler.py

Spawns and updates non-player objects:
- Static/animated decorative sprites
- NPC enemies

Also tracks NPC positions per-tick so pathfinding can avoid collisions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Set, Tuple, Type

from random import choices, randrange

import pygame as pg

from npc import CacoDemonNPC, CyberDemonNPC, NPC, SoldierNPC
from sprite_object import AnimatedSprite

if TYPE_CHECKING:
    from main import Game


class ObjectHandler:
    """Owns world objects (sprites + NPCs) and updates them each frame."""

    def __init__(self, game: Game) -> None:
        self.game = game

        self.sprite_list: list[AnimatedSprite] = []
        self.npc_list: list[NPC] = []

        self.npc_sprite_path = "resources/sprites/npc/"
        self.static_sprite_path = "resources/sprites/static_sprites/"
        self.anim_sprite_path = "resources/sprites/animated_sprites/"

        self.npc_positions: Set[Tuple[int, int]] = set()

        # -----------------------------------------------------------------
        # NPC spawning
        # -----------------------------------------------------------------
        self.enemies = 0  # npc count
        self.npc_types: list[Type[NPC]] = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
        self.weights = [70, 20, 10]
        self.restricted_area = {(i, j) for i in range(10) for j in range(10)}
        self.spawn_npc()

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

    def spawn_npc(self) -> None:
        """Randomly spawn NPCs onto walkable tiles."""
        for _ in range(self.enemies):
            npc_cls = choices(self.npc_types, self.weights)[0]
            pos = (randrange(self.game.map.cols), randrange(self.game.map.rows))

            while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                pos = (randrange(self.game.map.cols), randrange(self.game.map.rows))

            x, y = pos
            self.add_npc(npc_cls(self.game, pos=(x + 0.5, y + 0.5)))

    def check_win(self) -> None:
        """Restart the level when all NPCs are dead."""
        if not self.npc_positions:
            self.game.object_renderer.win()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def update(self) -> None:
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}

        for sprite in self.sprite_list:
            sprite.update()
        for npc in self.npc_list:
            npc.update()

        #self.check_win()

    def add_npc(self, npc: NPC) -> None:
        self.npc_list.append(npc)

    def add_sprite(self, sprite: AnimatedSprite) -> None:
        self.sprite_list.append(sprite)
