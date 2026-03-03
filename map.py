"""map.py

Grid map definition and world-map lookup structure.

- `mini_map` is a 2D grid: 0 means empty, 1..N are wall texture ids.
- `world_map` is a dict keyed by (x, y) tile coordinates for fast lookups.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Tuple

import pygame as pg

from map_io import load_map_json

if TYPE_CHECKING:
    from main import Game


# Optional: if this file exists, it will be used instead of the embedded map.
# This makes it easy to iterate on levels using map_editor.py.
DEFAULT_LEVEL_PATH = "resources/maps/level1.json"


# 0 = empty
# 1..5 = wall texture id
mini_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 3, 3, 3, 3, 0, 0, 0, 2, 2, 2, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 2, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 2, 0, 0, 1],
    [1, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 4, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 3, 1, 3, 1, 1, 1, 3, 0, 0, 3, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 0, 3, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 0, 3, 1, 1, 1],
    [1, 1, 3, 1, 1, 1, 1, 1, 1, 3, 0, 0, 3, 1, 1, 1],
    [1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 0, 0, 0, 3, 4, 0, 4, 3, 0, 1],
    [1, 0, 0, 5, 0, 0, 0, 0, 0, 0, 3, 0, 3, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 4, 0, 0, 0, 0, 0, 0, 4, 0, 0, 4, 0, 0, 0, 1],
    [1, 1, 3, 3, 0, 0, 3, 3, 1, 3, 3, 1, 3, 1, 1, 1],
    [1, 1, 1, 3, 0, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 3, 3, 4, 0, 0, 4, 3, 3, 3, 3, 3, 3, 3, 3, 1],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
]


class Map:
    """Holds the level grid and builds a fast lookup structure for walls."""

    def __init__(self, game: Game) -> None:
        self.game = game

        self.mini_map = self._load_or_default()
        self.world_map: Dict[Tuple[int, int], int] = {}

        self.rows = len(self.mini_map)
        self.cols = len(self.mini_map[0]) if self.rows else 0

        self._build_world_map()

    def _load_or_default(self):
        try:
            from pathlib import Path

            p = Path(DEFAULT_LEVEL_PATH)
            if p.exists():
                return load_map_json(p).grid
        except Exception:
            # If anything goes wrong, fall back to the embedded map.
            pass
        return mini_map

    def _build_world_map(self) -> None:
        for j, row in enumerate(self.mini_map):
            for i, value in enumerate(row):
                if value:
                    self.world_map[(i, j)] = int(value)

    def draw(self) -> None:
        """Debug 2D top-down view of wall tiles."""
        for x, y in self.world_map:
            pg.draw.rect(self.game.screen, "darkgray", (x * 100, y * 100, 100, 100), 2)
