"""map.py

Grid map definition and world-map lookup structure.

- `mini_map` is a 2D grid: 0 means empty, 1..N are wall texture ids.
- `world_map` is a dict keyed by (x, y) tile coordinates for fast lookups.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Tuple

import pygame as pg

from map_io import load_map_json
from map_editor import value_to_color, MAX_TILE
from settings import WIDTH, HEIGHT

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

    def draw(
        self,
        margin: int = 12,
        max_size_ratio: float = 0.30,  # 30% of the screen (width/height)
        border_px: int = 1,
    ) -> pg.Rect:
        """
        Draw a scaled debug view of the map (walls only) in the top-left corner.

        The map is scaled to fit within a box sized as a fraction of the screen,
        so larger/smaller custom maps won't render off-screen.

        Args:
            margin: Padding from the top-left corner in pixels.
            max_size_ratio: Maximum fraction of screen width/height used for minimap.
            border_px: Rectangle outline thickness for wall cells.

        Returns:
            The pygame.Rect area occupied by the minimap (useful for debugging/UI layout).
        """
        surf = self.game.screen
        screen_w, screen_h = surf.get_size()

        # Minimap bounding box (fit map into this)
        max_w = int(screen_w * max_size_ratio)
        max_h = int(screen_h * max_size_ratio)

        # Avoid division by zero on weird/empty maps
        cols = max(1, int(self.cols))
        rows = max(1, int(self.rows))

        # Uniform cell size so the whole map fits
        cell = max(2, min(max_w // cols, max_h // rows))

        map_px_w = cols * cell
        map_px_h = rows * cell

        x0 = WIDTH - margin - map_px_w
        y0 = margin # HEIGHT - margin - map_px_h
        minimap_rect = pg.Rect(x0, y0, map_px_w, map_px_h)

        # Draw a background + outline so it’s readable
        pg.draw.rect(surf, (0, 0, 0), minimap_rect)  # background
        pg.draw.rect(surf, "white", minimap_rect, 1)  # border

        # Draw wall cells
        for (x, y), value in self.world_map.items():
            # negative coords
            if x < 0 or y < 0:
                continue

            rx = x0 + x * cell
            ry = y0 + y * cell
            pg.draw.rect(surf, value_to_color(value, MAX_TILE), (rx, ry, cell, cell), border_px)

        return minimap_rect, cell
