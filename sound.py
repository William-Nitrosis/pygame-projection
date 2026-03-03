"""sound.py

Audio loading and simple sound effect handles.

This module loads:
- music (theme)
- weapon, NPC and player SFX
"""

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

        self.shotgun = pg.mixer.Sound(self.path + "shotgun.wav")
        self.npc_pain = pg.mixer.Sound(self.path + "npc_pain.wav")
        self.npc_death = pg.mixer.Sound(self.path + "npc_death.wav")
        self.npc_shot = pg.mixer.Sound(self.path + "npc_attack.wav")
        self.npc_shot.set_volume(0.2)

        self.player_pain = pg.mixer.Sound(self.path + "player_pain.wav")

        pg.mixer.music.load(self.path + "theme.mp3")
        pg.mixer.music.set_volume(0.3)
