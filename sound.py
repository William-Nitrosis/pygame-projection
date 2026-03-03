from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Game

import pygame as pg


class Sound:
    def __init__(self, game: Game):
        self.game = game
        pg.mixer.init()
        self.path = "resources/sound/"
        self.shotgun = pg.mixer.Sound(self.path + "shotgun.wav")
        self.npc_pain = pg.mixer.Sound(self.path + "npc_pain.wav")
        self.npc_death = pg.mixer.Sound(self.path + "npc_death.wav")
        self.npc_shot = pg.mixer.Sound(self.path + "npc_attack.wav")
        self.npc_shot.set_volume(0.2)
        self.player_pain = pg.mixer.Sound(self.path + "player_pain.wav")
        self.theme = pg.mixer.music.load(self.path + "theme.mp3")
        pg.mixer.music.set_volume(0.3)
