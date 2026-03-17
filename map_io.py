"""map_io.py

Helpers for loading/saving grid-based maps.

The runtime expects:
- A 2D grid (list of rows), where 0 is empty and 1..N are wall/texture ids.
- The game builds a `world_map` dict from the grid for fast collision/raycast tests.

The map editor (map_editor.py) also uses this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Sequence


Grid = List[List[int]]


@dataclass(frozen=True)
class MapData:
    """Map payload stored on disk."""

    grid: Grid
    spawn: Optional[tuple[float, float]] = None
    meta: Optional[dict[str, Any]] = None


def normalize_grid(grid: Sequence[Sequence[int]]) -> Grid:
    """Return a defensive copy of `grid` with all values coerced to ints >= 0."""
    out: Grid = []
    for row in grid:
        out_row: List[int] = []
        for v in row:
            iv = int(v)
            out_row.append(iv if iv >= 0 else 0)
        out.append(out_row)
    return out


def load_map_json(path: str | Path) -> MapData:
    """Load a map from JSON.

    Supported JSON shapes:
    1) {"grid": [[...]], "spawn": [x,y], "meta": {...}}
    2) [[...]]  (grid only)
    """
    import json

    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))

    if isinstance(data, list):
        grid = normalize_grid(data)
        return MapData(grid=grid)

    if not isinstance(data, dict) or "grid" not in data:
        raise ValueError(f"Invalid map JSON format: {p}")

    grid = normalize_grid(data["grid"])
    spawn = None
    if isinstance(data.get("spawn"), list) and len(data["spawn"]) == 2:
        spawn = (float(data["spawn"][0]), float(data["spawn"][1]))
    meta = data.get("meta") if isinstance(data.get("meta"), dict) else None
    return MapData(grid=grid, spawn=spawn, meta=meta)


def save_map_json(path: str | Path, map_data: MapData) -> None:
    """Save a map to JSON."""
    import json

    p = Path(path)
    payload: dict[str, Any] = {"grid": map_data.grid}
    if map_data.spawn is not None:
        payload["spawn"] = [map_data.spawn[0], map_data.spawn[1]]
    if map_data.meta is not None:
        payload["meta"] = map_data.meta

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
