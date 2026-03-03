"""settings.py

Central configuration for the raycasting "DOOM-like" pygame project.

Notes:
- `delta_time` used throughout the project is `Clock.tick(FPS)` (milliseconds).
  Movement / animation constants in this repo are tuned for that.
- Empty tiles in maps should be `0` (falsy). Wall tiles should be 1..N (truthy)
  where the value selects the wall texture.
"""

from __future__ import annotations

import math
from typing import Tuple

# ---------------------------------------------------------------------------
# Window / timing
# ---------------------------------------------------------------------------

WIDTH: int = 1600
HEIGHT: int = 900
RES = (WIDTH, HEIGHT)
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2

# FPS=0 means "uncapped" for pygame's Clock.tick.
FPS: int = 0

# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

PLAYER_POS: Tuple[float, float] = (1.5, 5.0)  # map-space coordinates
PLAYER_ANGLE: float = 0.0

# IMPORTANT: This project treats delta_time as milliseconds.
PLAYER_SPEED: float = 0.004
PLAYER_ROT_SPEED: float = 0.002

# Used for collision checks (tuned with ms delta_time).
PLAYER_SIZE_SCALE: float = 60.0
PLAYER_MAX_HEALTH: int = 100

# ---------------------------------------------------------------------------
# Mouse look
# ---------------------------------------------------------------------------

MOUSE_SENSITIVITY: float = 0.0003
MOUSE_MAX_REL: int = 40
MOUSE_BORDER_LEFT: int = 100
MOUSE_BORDER_RIGHT: int = WIDTH - MOUSE_BORDER_LEFT

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

FLOOR_COLOR: str = "#292929"

# ---------------------------------------------------------------------------
# Raycasting
# ---------------------------------------------------------------------------

FOV: float = math.pi / 3
HALF_FOV: float = FOV / 2

NUM_RAYS: int = WIDTH // 2
HALF_NUM_RAYS: int = NUM_RAYS // 2
DELTA_ANGLE: float = FOV / NUM_RAYS

MAX_DEPTH: int = 20

SCREEN_DIST: float = HALF_WIDTH / math.tan(HALF_FOV)
SCALE: int = WIDTH // NUM_RAYS

# ---------------------------------------------------------------------------
# Textures
# ---------------------------------------------------------------------------

TEXTURE_SIZE: int = 256
HALF_TEXTURE_SIZE: int = TEXTURE_SIZE // 2
