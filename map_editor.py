"""map_editor.py

A tiny pygame-based grid map editor for the raycasting project.

Controls
- Left click: paint selected wall id
- Right click / Middle click: erase to 0
- Mouse wheel / [ and ]: change selected wall id (0..9)
- G: toggle grid lines
- S: save JSON
- L: load JSON (revert unsaved changes)
- R: fill rectangle (click-drag) with current id
- ESC: quit

Usage
    python map_editor.py
    python map_editor.py --path resources/maps/level1.json --cols 32 --rows 32 --cell 24

Notes
- The runtime will automatically load DEFAULT_LEVEL_PATH if it exists (see map.py).
"""

from __future__ import annotations

import argparse
import colorsys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import pygame as pg

from map_io import MapData, load_map_json, save_map_json, normalize_grid

MAX_TILE = 8


@dataclass
class EditorState:
    selected: int = 1
    show_grid: bool = True
    dragging: bool = False
    drag_start: Optional[Tuple[int, int]] = None


def value_to_color(v: int, max_v: int) -> tuple[int, int, int]:
    t = v / max_v  # normalize 0 -> 1

    r, g, b = colorsys.hsv_to_rgb(t, 0.85, 1.0)

    return (
        int(r * 255),
        int(g * 255),
        int(b * 255),
    )


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def new_grid(cols: int, rows: int) -> list[list[int]]:
    return [[0 for _ in range(cols)] for _ in range(rows)]


def draw_text(surf: pg.Surface, text: str, x: int, y: int) -> None:
    font = pg.font.SysFont("consolas", 18)
    img = font.render(text, True, (240, 240, 240))
    surf.blit(img, (x, y))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="resources/maps/level1.json")
    parser.add_argument("--cols", type=int, default=32)
    parser.add_argument("--rows", type=int, default=32)
    parser.add_argument("--cell", type=int, default=24)
    args = parser.parse_args()

    map_path = Path(args.path)

    pg.init()
    pg.display.set_caption("PyGame Map Editor")

    state = EditorState()

    # load or create
    if map_path.exists():
        md = load_map_json(map_path)
        grid = md.grid
    else:
        grid = new_grid(args.cols, args.rows)

    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    cell = int(args.cell)

    ui_h = 80
    screen = pg.display.set_mode((cols * cell, rows * cell + ui_h))
    clock = pg.time.Clock()

    def save() -> None:
        save_map_json(map_path, MapData(grid=normalize_grid(grid)))
        pg.display.set_caption(f"PyGame Map Editor - saved {map_path}")

    def reload() -> None:
        nonlocal grid
        if map_path.exists():
            grid = load_map_json(map_path).grid

    def tile_at_mouse() -> Optional[Tuple[int, int]]:
        mx, my = pg.mouse.get_pos()
        if my >= rows * cell:
            return None
        tx = mx // cell
        ty = my // cell
        if 0 <= tx < cols and 0 <= ty < rows:
            return tx, ty
        return None

    def paint_rect(a: Tuple[int, int], b: Tuple[int, int], value: int) -> None:
        x0, y0 = a
        x1, y1 = b
        minx, maxx = sorted((x0, x1))
        miny, maxy = sorted((y0, y1))
        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                grid[y][x] = value

    running = True
    while running:
        clock.tick(60)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_g:
                    state.show_grid = not state.show_grid
                elif event.key == pg.K_s:
                    save()
                elif event.key == pg.K_l:
                    reload()
                elif event.key == pg.K_LEFTBRACKET:
                    state.selected = clamp(state.selected - 1, 0, MAX_TILE)
                elif event.key == pg.K_RIGHTBRACKET:
                    state.selected = clamp(state.selected + 1, 0, MAX_TILE)

            if event.type == pg.MOUSEWHEEL:
                state.selected = clamp(state.selected + event.y, 0, MAX_TILE)

            if event.type == pg.MOUSEBUTTONDOWN:
                tile = tile_at_mouse()
                if tile is None:
                    continue

                if event.button == 1:
                    # start drag fill mode with shift, otherwise paint single
                    mods = pg.key.get_mods()
                    if mods & pg.KMOD_SHIFT:
                        state.dragging = True
                        state.drag_start = tile
                    else:
                        x, y = tile
                        grid[y][x] = state.selected
                elif event.button in (2, 3):
                    x, y = tile
                    grid[y][x] = 0

            if event.type == pg.MOUSEBUTTONUP:
                if (
                    event.button == 1
                    and state.dragging
                    and state.drag_start is not None
                ):
                    tile = tile_at_mouse()
                    if tile is not None:
                        paint_rect(state.drag_start, tile, state.selected)
                    state.dragging = False
                    state.drag_start = None

        # continuous paint while holding mouse
        tile = tile_at_mouse()
        buttons = pg.mouse.get_pressed(3)
        if tile is not None:
            x, y = tile
            if buttons[0] and not state.dragging:
                grid[y][x] = state.selected
            if buttons[2]:
                grid[y][x] = 0

        # draw grid
        screen.fill((10, 10, 10))
        for y in range(rows):
            for x in range(cols):
                v = grid[y][x]
                if v == 0:
                    continue
                # simple value->color mapping
                c = value_to_color(v, MAX_TILE)
                pg.draw.rect(screen, c, (x * cell, y * cell, cell, cell))

        if state.show_grid:
            for x in range(cols + 1):
                pg.draw.line(
                    screen, (35, 35, 35), (x * cell, 0), (x * cell, rows * cell), 1
                )
            for y in range(rows + 1):
                pg.draw.line(
                    screen, (35, 35, 35), (0, y * cell), (cols * cell, y * cell), 1
                )

        # UI panel
        pg.draw.rect(screen, (20, 20, 20), (0, rows * cell, cols * cell, ui_h))
        draw_text(
            screen,
            f"Selected wall id: {state.selected}   (wheel / [ ])",
            10,
            rows * cell + 10,
        )
        draw_text(
            screen,
            f"Left=paint  Right/Middle=erase  Shift+Drag=rect-fill  S=save  L=load  G=grid",
            10,
            rows * cell + 34,
        )
        draw_text(screen, f"Path: {map_path}", 10, rows * cell + 56)

        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
