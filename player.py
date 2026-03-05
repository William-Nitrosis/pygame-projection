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
    PLAYER_POS,
    PLAYER_SIZE_SCALE,
    PLAYER_SPEED,
)

if TYPE_CHECKING:
    from main import Game


class Player:
    """Represents the player controller and state."""

    def __init__(self, game: Game) -> None:
        self.game = game

        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE

        self.rel: int = 0

        # diagonal movement correction
        self.diag_move_corr = 1 / math.sqrt(2)

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

    def draw(self, minimap_rect: pg.Rect, cell: int) -> None:
        """
        Draw the player position and facing direction on the minimap.
        """

        x0 = minimap_rect.x
        y0 = minimap_rect.y

        px = x0 + self.x * cell
        py = y0 + self.y * cell

        # Direction line
        line_len = cell * 1
        dx = math.cos(self.angle) * line_len
        dy = math.sin(self.angle) * line_len

        pg.draw.line(
            self.game.screen,
            "yellow",
            (px, py),
            (px + dx, py + dy),
            1,
        )

        # Player dot
        pg.draw.circle(self.game.screen, "green", (int(px), int(py)), max(3, cell // 3))

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

    @property
    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    @property
    def map_pos(self) -> tuple[int, int]:
        return int(self.x), int(self.y)
