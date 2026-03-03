"""npc.py

Enemy NPC logic:
- Uses billboard sprites with animations for idle/walk/attack/pain/death.
- Uses grid-based pathfinding (BFS) to move toward the player.
- Uses a raycast test to determine if the NPC has line-of-sight to the player.

This is intentionally simple and "arcade DOOM-like" rather than a full 3D AI system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import math
from random import randint, random

import pygame as pg

from settings import HALF_WIDTH, MAX_DEPTH
from sprite_object import AnimatedSprite

if TYPE_CHECKING:
    from main import Game


EPS = 1e-6


class NPC(AnimatedSprite):
    """Base enemy class with simple state + animation handling."""

    def __init__(
        self,
        game: Game,
        path: str = "resources/sprites/npc/soldier/0.png",
        pos: tuple[float, float] = (10.5, 5.5),
        scale: float = 0.6,
        shift: float = 0.38,
        animation_time: int = 180,
    ) -> None:
        super().__init__(game, path, pos, scale, shift, animation_time)

        # animation sets
        self.attack_images = self.get_images(self.path + "/attack")
        self.death_images = self.get_images(self.path + "/death")
        self.idle_images = self.get_images(self.path + "/idle")
        self.pain_images = self.get_images(self.path + "/pain")
        self.walk_images = self.get_images(self.path + "/walk")

        # tuning / stats
        self.attack_dist = randint(3, 6)
        self.speed = 0.03
        self.size = 20  # collision "radius" in map-space scale
        self.health = 100
        self.attack_damage = 10
        self.accuracy = 0.15

        # state
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.player_search_trigger = False

    def update(self) -> None:
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()
        # self.draw_ray_cast()  # debug

    # ------------------------------------------------------------------
    # Movement / collision
    # ------------------------------------------------------------------

    def check_wall(self, x: int, y: int) -> bool:
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx: float, dy: float) -> None:
        if self.check_wall(int(self.x + dx * self.size), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * self.size)):
            self.y += dy

    def movement(self) -> None:
        next_pos = self.game.pathfinding.get_path(
            self.map_pos, self.game.player.map_pos
        )
        next_x, next_y = next_pos

        if next_pos not in self.game.object_handler.npc_positions:
            angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.check_wall_collision(dx, dy)

    # ------------------------------------------------------------------
    # Combat / state
    # ------------------------------------------------------------------

    def attack(self) -> None:
        if self.animation_trigger:
            self.game.sound.npc_shot.play()
            if random() < self.accuracy:
                self.game.player.get_damage(self.attack_damage)

    def animate_death(self) -> None:
        if not self.alive:
            if (
                self.game.global_trigger
                and self.frame_counter < len(self.death_images) - 1
            ):
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1

    def animate_pain(self) -> None:
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def check_hit_in_npc(self) -> None:
        """Check whether the player's shot intersects the NPC sprite on screen."""
        if self.ray_cast_value and self.game.player.shot:
            if (
                HALF_WIDTH - self.sprite_half_width
                < self.screen_x
                < HALF_WIDTH + self.sprite_half_width
            ):
                self.game.sound.npc_pain.play()
                self.game.player.shot = False
                self.pain = True
                self.health -= self.game.weapon.damage
                self.check_health()

    def check_health(self) -> None:
        if self.health < 1:
            self.alive = False
            self.game.sound.npc_death.play()

    def run_logic(self) -> None:
        if self.alive:
            self.ray_cast_value = self.ray_cast_player_npc()
            self.check_hit_in_npc()

            if self.pain:
                self.animate_pain()
                return

            if self.ray_cast_value:
                self.player_search_trigger = True
                if self.dist < self.attack_dist:
                    self.animate(self.attack_images)
                    self.attack()
                else:
                    self.animate(self.walk_images)
                    self.movement()
                return

            if self.player_search_trigger:
                self.animate(self.walk_images)
                self.movement()
                return

            self.animate(self.idle_images)
        else:
            self.animate_death()

    @property
    def map_pos(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    # ------------------------------------------------------------------
    # LOS ray cast (NPC -> player)
    # ------------------------------------------------------------------

    def ray_cast_player_npc(self) -> bool:
        """Return True if the NPC has line-of-sight to the player."""
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_v = 0.0
        wall_dist_h = 0.0
        player_dist_v = 0.0
        player_dist_h = 0.0

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.theta

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)
        if abs(sin_a) < EPS:
            sin_a = EPS if sin_a >= 0 else -EPS
        if abs(cos_a) < EPS:
            cos_a = EPS if cos_a >= 0 else -EPS

        # horizontals
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)
        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for _ in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == self.map_pos:
                player_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)
        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a

        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for _ in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == self.map_pos:
                player_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_v, player_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        return (0 < player_dist < wall_dist) or (not wall_dist)

    def draw_ray_cast(self) -> None:
        """Debug: visualize the LOS ray on the 2D map."""
        pg.draw.circle(self.game.screen, "red", (100 * self.x, 100 * self.y), 15)
        if self.ray_cast_player_npc():
            pg.draw.line(
                self.game.screen,
                "orange",
                (100 * self.game.player.x, 100 * self.game.player.y),
                (100 * self.x, 100 * self.y),
                2,
            )


class SoldierNPC(NPC):
    """Default enemy (balanced)."""

    def __init__(
        self,
        game: Game,
        path: str = "resources/sprites/npc/soldier/0.png",
        pos: tuple[float, float] = (10.5, 5.5),
        scale: float = 0.6,
        shift: float = 0.38,
        animation_time: int = 180,
    ) -> None:
        super().__init__(game, path, pos, scale, shift, animation_time)


class CacoDemonNPC(NPC):
    """Fast melee-ish enemy with higher damage."""

    def __init__(
        self,
        game: Game,
        path: str = "resources/sprites/npc/caco_demon/0.png",
        pos: tuple[float, float] = (10.5, 6.5),
        scale: float = 0.7,
        shift: float = 0.27,
        animation_time: int = 250,
    ) -> None:
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 1.0
        self.health = 150
        self.attack_damage = 25
        self.speed = 0.05
        self.accuracy = 0.35


class CyberDemonNPC(NPC):
    """Tanky enemy with long range."""

    def __init__(
        self,
        game: Game,
        path: str = "resources/sprites/npc/cyber_demon/0.png",
        pos: tuple[float, float] = (11.5, 6.0),
        scale: float = 1.0,
        shift: float = 0.04,
        animation_time: int = 210,
    ) -> None:
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 6
        self.health = 350
        self.attack_damage = 15
        self.speed = 0.055
        self.accuracy = 0.25
