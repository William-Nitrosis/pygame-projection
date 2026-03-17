"""map_editor.py

A tiny pygame-based grid map editor for the raycasting project.

Controls
- TAB: cycle mode (WALL / OBJECT / SPAWN)
- Left click:
    WALL  -> paint selected wall id
    OBJECT -> place selected object preset
    SPAWN -> set player spawn
- Right click / Middle click:
    WALL  -> erase wall to 0
    OBJECT -> remove object on tile
    SPAWN -> clear spawn if clicked on it
- Mouse wheel / [ and ]:
    WALL  -> change selected wall id
    OBJECT -> change selected object preset
- Shift + Left drag (WALL mode): rectangle fill
- G: toggle grid lines
- S: save JSON
- L: load JSON (revert unsaved changes)
- T: in OBJECT mode, toggle goal on object under mouse
- ESC: quit

Usage
    python map_editor.py
    python map_editor.py --path resources/maps/level1.json --cols 32 --rows 32 --cell 24
"""

from __future__ import annotations

import argparse
import colorsys
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import pygame as pg

from map_io import MapData, load_map_json, normalize_grid, save_map_json

MAX_TILE = 8


@dataclass
class EditorState:
    selected: int = 1
    show_grid: bool = True
    dragging: bool = False
    drag_start: Optional[tuple[int, int]] = None
    mode_index: int = 0
    selected_object_index: int = 0


MODES = ["WALL", "OBJECT", "SPAWN"]

OBJECT_PRESETS: list[dict[str, Any]] = [
    {
        "label": "Goal Green Light",
        "kind": "animated",
        "sprite": "green_light",
        "goal": True,
        "trigger_radius": 0.7,
        "scale": 0.8,
        "shift": 0.16,
        "animation_time": 120,
    },
    {
        "label": "Red Light",
        "kind": "animated",
        "sprite": "red_light",
        "goal": False,
        "trigger_radius": 0.6,
        "scale": 0.8,
        "shift": 0.16,
        "animation_time": 120,
    },
    {
        "label": "Candlebra",
        "kind": "static",
        "sprite": "candlebra.png",
        "goal": False,
        "trigger_radius": 0.6,
        "scale": 0.7,
        "shift": 0.27,
    },
]


def value_to_color(v: int, max_v: int) -> tuple[int, int, int]:
    t = v / max_v if max_v > 0 else 0.0
    r, g, b = colorsys.hsv_to_rgb(t, 0.85, 1.0)
    return int(r * 255), int(g * 255), int(b * 255)


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def new_grid(cols: int, rows: int) -> list[list[int]]:
    return [[0 for _ in range(cols)] for _ in range(rows)]


def draw_text(
    surf: pg.Surface,
    text: str,
    x: int,
    y: int,
    color: tuple[int, int, int] = (240, 240, 240),
) -> None:
    font = pg.font.SysFont("consolas", 18)
    img = font.render(text, True, color)
    surf.blit(img, (x, y))


def tile_center(tile_x: int, tile_y: int) -> tuple[float, float]:
    return tile_x + 0.5, tile_y + 0.5


def pos_to_tile(pos: tuple[float, float]) -> tuple[int, int]:
    return int(pos[0]), int(pos[1])


def make_object_from_preset(
    preset: dict[str, Any],
    tile_x: int,
    tile_y: int,
) -> dict[str, Any]:
    obj = deepcopy(preset)
    obj["pos"] = [tile_x + 0.5, tile_y + 0.5]
    obj.pop("label", None)
    return obj


def find_object_at_tile(
    sprites: list[dict[str, Any]],
    tile_x: int,
    tile_y: int,
) -> Optional[int]:
    for index, sprite in enumerate(sprites):
        pos = sprite.get("pos")
        if not isinstance(pos, (list, tuple)) or len(pos) != 2:
            continue
        if int(float(pos[0])) == tile_x and int(float(pos[1])) == tile_y:
            return index
    return None


def ensure_meta(meta: Optional[dict[str, Any]]) -> dict[str, Any]:
    if isinstance(meta, dict):
        out = deepcopy(meta)
    else:
        out = {}

    sprites = out.get("sprites")
    if not isinstance(sprites, list):
        out["sprites"] = []
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="resources/maps/level4.json")
    parser.add_argument("--cols", type=int, default=32)
    parser.add_argument("--rows", type=int, default=32)
    parser.add_argument("--cell", type=int, default=24)
    args = parser.parse_args()

    map_path = Path(args.path)

    pg.init()
    pg.display.set_caption("PyGame Map Editor")

    state = EditorState()

    if map_path.exists():
        md = load_map_json(map_path)
        grid = md.grid
        spawn = md.spawn
        meta = ensure_meta(md.meta)
    else:
        grid = new_grid(args.cols, args.rows)
        spawn = None
        meta = {"sprites": []}

    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    cell = int(args.cell)

    sprites: list[dict[str, Any]] = meta["sprites"]

    ui_h = 120
    screen = pg.display.set_mode((cols * cell, rows * cell + ui_h))
    clock = pg.time.Clock()

    def current_mode() -> str:
        return MODES[state.mode_index]

    def current_object_preset() -> dict[str, Any]:
        return OBJECT_PRESETS[state.selected_object_index]

    def save() -> None:
        save_map_json(
            map_path,
            MapData(
                grid=normalize_grid(grid),
                spawn=spawn,
                meta={"sprites": sprites},
            ),
        )
        pg.display.set_caption(f"PyGame Map Editor - saved {map_path}")

    def reload() -> None:
        nonlocal grid, spawn, meta, sprites, rows, cols, screen
        if map_path.exists():
            md2 = load_map_json(map_path)
            grid = md2.grid
            spawn = md2.spawn
            meta = ensure_meta(md2.meta)
            sprites = meta["sprites"]
            rows = len(grid)
            cols = len(grid[0]) if rows else 0
            screen = pg.display.set_mode((cols * cell, rows * cell + ui_h))
            pg.display.set_caption(f"PyGame Map Editor - loaded {map_path}")

    def tile_at_mouse() -> Optional[tuple[int, int]]:
        mx, my = pg.mouse.get_pos()
        if my >= rows * cell:
            return None
        tx = mx // cell
        ty = my // cell
        if 0 <= tx < cols and 0 <= ty < rows:
            return tx, ty
        return None

    def paint_rect(a: tuple[int, int], b: tuple[int, int], value: int) -> None:
        x0, y0 = a
        x1, y1 = b
        minx, maxx = sorted((x0, x1))
        miny, maxy = sorted((y0, y1))
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                grid[yy][xx] = value

    def place_object(tile_x: int, tile_y: int) -> None:
        existing = find_object_at_tile(sprites, tile_x, tile_y)
        obj = make_object_from_preset(current_object_preset(), tile_x, tile_y)
        if existing is None:
            sprites.append(obj)
        else:
            sprites[existing] = obj

    def remove_object(tile_x: int, tile_y: int) -> None:
        existing = find_object_at_tile(sprites, tile_x, tile_y)
        if existing is not None:
            sprites.pop(existing)

    def toggle_goal(tile_x: int, tile_y: int) -> None:
        existing = find_object_at_tile(sprites, tile_x, tile_y)
        if existing is None:
            return
        current = bool(sprites[existing].get("goal", False))
        sprites[existing]["goal"] = not current

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
                elif event.key == pg.K_TAB:
                    state.mode_index = (state.mode_index + 1) % len(MODES)
                    state.dragging = False
                    state.drag_start = None
                elif event.key == pg.K_t and current_mode() == "OBJECT":
                    tile = tile_at_mouse()
                    if tile is not None:
                        toggle_goal(tile[0], tile[1])
                elif current_mode() == "WALL":
                    if event.key == pg.K_LEFTBRACKET:
                        state.selected = clamp(state.selected - 1, 0, MAX_TILE)
                    elif event.key == pg.K_RIGHTBRACKET:
                        state.selected = clamp(state.selected + 1, 0, MAX_TILE)
                elif current_mode() == "OBJECT":
                    if event.key == pg.K_LEFTBRACKET:
                        state.selected_object_index = (
                            state.selected_object_index - 1
                        ) % len(OBJECT_PRESETS)
                    elif event.key == pg.K_RIGHTBRACKET:
                        state.selected_object_index = (
                            state.selected_object_index + 1
                        ) % len(OBJECT_PRESETS)

            if event.type == pg.MOUSEWHEEL:
                if current_mode() == "WALL":
                    state.selected = clamp(state.selected + event.y, 0, MAX_TILE)
                elif current_mode() == "OBJECT":
                    state.selected_object_index = (
                        state.selected_object_index + event.y
                    ) % len(OBJECT_PRESETS)

            if event.type == pg.MOUSEBUTTONDOWN:
                tile = tile_at_mouse()
                if tile is None:
                    continue

                tx, ty = tile
                mode = current_mode()

                if event.button == 1:
                    if mode == "WALL":
                        mods = pg.key.get_mods()
                        if mods & pg.KMOD_SHIFT:
                            state.dragging = True
                            state.drag_start = tile
                        else:
                            grid[ty][tx] = state.selected
                    elif mode == "OBJECT":
                        place_object(tx, ty)
                    elif mode == "SPAWN":
                        spawn = tile_center(tx, ty)

                elif event.button in (2, 3):
                    if mode == "WALL":
                        grid[ty][tx] = 0
                    elif mode == "OBJECT":
                        remove_object(tx, ty)
                    elif mode == "SPAWN":
                        if spawn is not None and pos_to_tile(spawn) == (tx, ty):
                            spawn = None

            if event.type == pg.MOUSEBUTTONUP:
                if (
                    event.button == 1
                    and current_mode() == "WALL"
                    and state.dragging
                    and state.drag_start is not None
                ):
                    tile = tile_at_mouse()
                    if tile is not None:
                        paint_rect(state.drag_start, tile, state.selected)
                    state.dragging = False
                    state.drag_start = None

        tile = tile_at_mouse()
        buttons = pg.mouse.get_pressed(3)
        if tile is not None and current_mode() == "WALL":
            tx, ty = tile
            if buttons[0] and not state.dragging:
                grid[ty][tx] = state.selected
            if buttons[2]:
                grid[ty][tx] = 0

        screen.fill((10, 10, 10))

        for y in range(rows):
            for x in range(cols):
                v = grid[y][x]
                if v == 0:
                    continue
                c = value_to_color(v, MAX_TILE)
                pg.draw.rect(screen, c, (x * cell, y * cell, cell, cell))

        # spawn marker
        if spawn is not None:
            sx, sy = spawn
            px = int(sx * cell)
            py = int(sy * cell)
            pg.draw.circle(screen, (0, 220, 120), (px, py), max(4, cell // 3), 2)
            pg.draw.line(screen, (0, 220, 120), (px - 6, py), (px + 6, py), 2)
            pg.draw.line(screen, (0, 220, 120), (px, py - 6), (px, py + 6), 2)

        # object markers
        for sprite in sprites:
            pos = sprite.get("pos")
            if not isinstance(pos, (list, tuple)) or len(pos) != 2:
                continue

            sx = float(pos[0])
            sy = float(pos[1])

            px = int(sx * cell)
            py = int(sy * cell)

            is_goal = bool(sprite.get("goal", False))
            kind = str(sprite.get("kind", "animated")).lower()

            if kind == "static":
                color = (80, 180, 255)
            else:
                color = (255, 200, 80)

            if is_goal:
                color = (80, 255, 120)

            radius = max(4, cell // 4)
            pg.draw.circle(screen, color, (px, py), radius)
            pg.draw.circle(screen, (20, 20, 20), (px, py), radius, 1)

            if is_goal:
                pg.draw.circle(screen, (255, 255, 255), (px, py), radius + 3, 1)

        if state.show_grid:
            for x in range(cols + 1):
                pg.draw.line(
                    screen,
                    (35, 35, 35),
                    (x * cell, 0),
                    (x * cell, rows * cell),
                    1,
                )
            for y in range(rows + 1):
                pg.draw.line(
                    screen,
                    (35, 35, 35),
                    (0, y * cell),
                    (cols * cell, y * cell),
                    1,
                )

        hovered_tile = tile_at_mouse()
        if hovered_tile is not None:
            hx, hy = hovered_tile
            pg.draw.rect(
                screen,
                (255, 255, 255),
                (hx * cell, hy * cell, cell, cell),
                1,
            )

        pg.draw.rect(screen, (20, 20, 20), (0, rows * cell, cols * cell, ui_h))

        mode = current_mode()
        draw_text(
            screen,
            f"Mode: {mode}   TAB=cycle",
            10,
            rows * cell + 8,
            (255, 255, 120),
        )

        if mode == "WALL":
            draw_text(
                screen,
                f"Selected wall id: {state.selected}   (wheel / [ ])",
                10,
                rows * cell + 32,
            )
            draw_text(
                screen,
                "Left=paint  Right/Middle=erase  Shift+Drag=rect-fill",
                10,
                rows * cell + 56,
            )
        elif mode == "OBJECT":
            preset = current_object_preset()
            draw_text(
                screen,
                f"Selected object: {preset['label']}   (wheel / [ ])",
                10,
                rows * cell + 32,
            )
            draw_text(
                screen,
                "Left=place/replace  Right/Middle=remove  T=toggle goal",
                10,
                rows * cell + 56,
            )
        else:
            draw_text(
                screen,
                "Spawn mode: Left=set spawn  Right/Middle=clear spawn",
                10,
                rows * cell + 32,
            )

        draw_text(
            screen,
            "S=save  L=load  G=grid  ESC=quit",
            10,
            rows * cell + 80,
        )

        draw_text(screen, f"Path: {map_path}", 10, rows * cell + 100)

        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
