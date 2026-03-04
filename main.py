"""main.py

Entry point and high-level game loop.

This module owns the pygame init, window setup, and coordinates the major
subsystems (map, player, renderer, raycaster, NPC handler, audio, etc.).
"""

from __future__ import annotations

import sys

import pygame as pg

from settings import FPS, RES
from map import Map
from player import Player
from raycasting import RayCasting
from object_renderer import ObjectRenderer
from object_handler import ObjectHandler
from weapon import Weapon
from sound import Sound
from pathfinding import PathFinding


class Game:
    """Top-level game object that wires together all subsystems."""

    def __init__(self) -> None:
        pg.init()
        pg.mouse.set_visible(False)

        self.screen = pg.display.set_mode(RES)
        pg.display.set_caption("PyGame DOOM-style Raycaster")
        pg.event.set_grab(True)

        self.clock = pg.time.Clock()
        self.delta_time: int = 1  # milliseconds
        self.global_trigger: bool = False

        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)

        self.new_game()

    def new_game(self) -> None:
        """(Re)create game state for a new run."""
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)

        pg.mixer.music.play(-1)

    def update(self) -> None:
        """Update simulation and present the frame."""
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()

        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f"FPS: {self.clock.get_fps():.1f}")

    def draw(self) -> None:
        """Draw the current frame."""
        self.object_renderer.draw()
        self.weapon.draw()
        # Debug helpers:
        minimap_rect, cell = self.map.draw(max_size_ratio=0.9)
        self.player.draw(minimap_rect, cell)

    def check_events(self) -> None:
        """Process pygame events."""
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (
                event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
            ):
                pg.quit()
                sys.exit()

            if event.type == self.global_event:
                self.global_trigger = True

            self.player.single_fire_event(event)

    def run(self) -> None:
        """Main loop."""
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == "__main__":
    Game().run()
