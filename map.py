from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Tuple

import pygame as pg

from map_io import load_map_json
from map_editor import value_to_color, MAX_TILE
from settings import WIDTH

if TYPE_CHECKING:
    from main import Game


DEFAULT_LEVEL_PATH = "resources/maps/level1.json"


class Map:
    """Holds the level grid and level metadata loaded from JSON."""

    def __init__(self, game: Game, level_path: str = DEFAULT_LEVEL_PATH) -> None:
        self.game = game
        self.level_path = Path(level_path)

        self.mini_map: list[list[int]] = []
        self.world_map: Dict[Tuple[int, int], int] = {}

        self.spawn: tuple[float, float] | None = None
        self.meta: dict[str, Any] = {}

        self._load()
        self.rows = len(self.mini_map)
        self.cols = len(self.mini_map[0]) if self.rows else 0
        self._build_world_map()

    def _load(self) -> None:
        try:
            if self.level_path.exists():
                data = load_map_json(self.level_path)
                self.mini_map = data.grid
                self.spawn = data.spawn
                self.meta = data.meta or {}
                return
        except Exception:
            pass

        self.mini_map = []
        self.spawn = None
        self.meta = {}

    def _build_world_map(self) -> None:
        for j, row in enumerate(self.mini_map):
            for i, value in enumerate(row):
                if value:
                    self.world_map[(i, j)] = int(value)

    def draw(
        self,
        margin: int = 12,
        max_size_ratio: float = 0.30,
        border_px: int = 1,
    ) -> tuple[pg.Rect, int]:
        """Draw a scaled debug view of the map in the top-right corner."""
        surf = self.game.screen
        screen_w, screen_h = surf.get_size()

        max_w = int(screen_w * max_size_ratio)
        max_h = int(screen_h * max_size_ratio)

        cols = max(1, int(self.cols))
        rows = max(1, int(self.rows))

        cell = max(2, min(max_w // cols, max_h // rows))

        map_px_w = cols * cell
        map_px_h = rows * cell

        x0 = WIDTH - margin - map_px_w
        y0 = margin
        minimap_rect = pg.Rect(x0, y0, map_px_w, map_px_h)

        pg.draw.rect(surf, (0, 0, 0), minimap_rect)
        pg.draw.rect(surf, "white", minimap_rect, 1)

        for (x, y), value in self.world_map.items():
            if x < 0 or y < 0:
                continue

            rx = x0 + x * cell
            ry = y0 + y * cell
            pg.draw.rect(
                surf,
                value_to_color(value, MAX_TILE),
                (rx, ry, cell, cell),
                border_px,
            )

        return minimap_rect, cell