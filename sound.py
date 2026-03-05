from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from main import Game


class Sound:
    """Loads and owns pygame.mixer sound assets."""

    def __init__(self, game: Game) -> None:
        self.game = game

        if pg.mixer.get_init() is None:
            pg.mixer.init()

        self.path = "resources/sound/"

        pg.mixer.music.load(self.path + "theme.mp3")
        pg.mixer.music.set_volume(0.1)
