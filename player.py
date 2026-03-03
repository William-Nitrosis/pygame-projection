"""player.py

Player movement, input handling and health.

Movement is in map-space (tiles are 1x1). Collision is grid-based using the
Map.world_map lookup.

Important: this project uses `game.delta_time` in **milliseconds** (from
pygame.Clock.tick).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import math
import pygame as pg

from settings import (
    HALF_HEIGHT,
    HALF_WIDTH,
    MOUSE_BORDER_LEFT,
    MOUSE_BORDER_RIGHT,
    MOUSE_MAX_REL,
    MOUSE_SENSITIVITY,
    PLAYER_ANGLE,
    PLAYER_MAX_HEALTH,
    PLAYER_POS,
    PLAYER_SIZE_SCALE,
    PLAYER_SPEED,
    WIDTH,
)

if TYPE_CHECKING:
    from main import Game


class Player:
    """Represents the player controller and state."""

    def __init__(self, game: Game) -> None:
        self.game = game

        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE

        self.shot: bool = False

        self.health: int = PLAYER_MAX_HEALTH
        self.rel: int = 0

        self.health_recovery_delay_ms = 700
        self._health_time_prev = pg.time.get_ticks()

        # diagonal movement correction
        self.diag_move_corr = 1 / math.sqrt(2)

    # ---------------------------------------------------------------------
    # Health
    # ---------------------------------------------------------------------

    def recover_health(self) -> None:
        """Passive health regeneration."""
        if self._check_health_recovery_delay() and self.health < PLAYER_MAX_HEALTH:
            self.health += 1

    def _check_health_recovery_delay(self) -> bool:
        time_now = pg.time.get_ticks()
        if time_now - self._health_time_prev > self.health_recovery_delay_ms:
            self._health_time_prev = time_now
            return True
        return False

    def check_game_over(self) -> None:
        if self.health < 1:
            self.game.object_renderer.game_over()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def get_damage(self, damage: float) -> None:
        """Apply damage and trigger feedback."""
        self.health -= int(damage)
        self.game.object_renderer.player_damage()
        self.game.sound.player_pain.play()
        self.check_game_over()

    # ---------------------------------------------------------------------
    # Input
    # ---------------------------------------------------------------------

    def single_fire_event(self, event: pg.event.Event) -> None:
        """Handle single-shot fire input from mouse events."""
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if not self.shot and not self.game.weapon.reloading:
                self.game.sound.shotgun.play()
                self.shot = True
                self.game.weapon.reloading = True

    # ---------------------------------------------------------------------
    # Movement / collision
    # ---------------------------------------------------------------------

    def movement(self) -> None:
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)

        dx = 0.0
        dy = 0.0

        dt_ms = max(1, int(self.game.delta_time))
        speed = PLAYER_SPEED * dt_ms
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        keys = pg.key.get_pressed()
        keys_down = 0

        if keys[pg.K_w]:
            keys_down += 1
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            keys_down += 1
            dx -= speed_cos
            dy -= speed_sin
        if keys[pg.K_a]:
            keys_down += 1
            dx += speed_sin
            dy -= speed_cos
        if keys[pg.K_d]:
            keys_down += 1
            dx -= speed_sin
            dy += speed_cos

        # diagonal move correction
        if keys_down >= 2:
            dx *= self.diag_move_corr
            dy *= self.diag_move_corr

        self._check_wall_collision(dx, dy)
        self.angle %= math.tau

    def _is_walkable(self, x: int, y: int) -> bool:
        return (x, y) not in self.game.map.world_map

    def _check_wall_collision(self, dx: float, dy: float) -> None:
        dt_ms = max(1, int(self.game.delta_time))
        scale = PLAYER_SIZE_SCALE / dt_ms

        if self._is_walkable(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self._is_walkable(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    def draw(self) -> None:
        """Debug draw of the player in the top-down map view."""
        pg.draw.line(
            self.game.screen,
            "yellow",
            (self.x * 100, self.y * 100),
            (
                self.x * 100 + WIDTH * math.cos(self.angle),
                self.y * 100 + WIDTH * math.sin(self.angle),
            ),
            2,
        )
        pg.draw.circle(self.game.screen, "green", (self.x * 100, self.y * 100), 15)

    # ---------------------------------------------------------------------
    # Mouse look
    # ---------------------------------------------------------------------

    def mouse_control(self) -> None:
        mx, _ = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])

        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))

        self.angle += self.rel * MOUSE_SENSITIVITY * max(1, int(self.game.delta_time))

    # ---------------------------------------------------------------------
    # Tick
    # ---------------------------------------------------------------------

    def update(self) -> None:
        self.movement()
        self.mouse_control()
        self.recover_health()

    @property
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def map_pos(self) -> tuple[int, int]:
        return int(self.x), int(self.y)
