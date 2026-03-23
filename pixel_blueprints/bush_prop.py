DEFAULT_W = 16
DEFAULT_H = 16
BLUEPRINT_DISPLAY_NAME = 'Bush Prop'
BLUEPRINT_DESCRIPTION = 'A compact bush prop with seeded leaf breakup and a small trunk base for side-view or top-down scene dressing.'

import random

from pixel_art import engine as ep
from pixel_art.palettes import NATURE_PALETTE


BLUEPRINT_PALETTE_OVERRIDES = NATURE_PALETTE


def make_image(x, y, W, H, seed=None):
    rng_seed = (0 if seed is None else seed) * 6151 + x * 97 + y * 29
    rng = random.Random(rng_seed)
    cx = W // 2

    canopy = (
        ep.is_ellipse(x, y, cx, 7, 5, 4)
        or ep.is_ellipse(x, y, cx - 3, 8, 3, 3)
        or ep.is_ellipse(x, y, cx + 3, 8, 3, 3)
        or ep.is_ellipse(x, y, cx, 10, 6, 3)
    )

    trunk = ep.is_rect(x, y, cx - 1, 11, cx + 1, 14)
    shadow = ep.is_rect(x, y, 4, 15, 11, 15)

    if shadow and not canopy and not trunk:
        return 142

    if trunk:
        if y >= 13 or x == cx + 1:
            return 143
        return 144

    if not canopy:
        return 0

    if y <= 5 and abs(x - cx) <= 1:
        return 141

    if (x + y + rng.randint(0, 2)) % 6 == 0:
        return 141

    if rng.random() < 0.18 or y >= 10:
        return 142

    return 140