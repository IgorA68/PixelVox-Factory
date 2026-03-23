DEFAULT_W = 16
DEFAULT_H = 16
BLUEPRINT_DISPLAY_NAME = 'Grass Tile'
BLUEPRINT_DESCRIPTION = 'A top-down grass tile with seeded blade clustering, dirt breakup, and a few subtle stones for terrain prototyping.'

import random

from pixel_art.palettes import NATURE_PALETTE


BLUEPRINT_PALETTE_OVERRIDES = NATURE_PALETTE


def make_image(x, y, W, H, seed=None):
    rng_seed = (0 if seed is None else seed) * 7919 + x * 131 + y * 17
    rng = random.Random(rng_seed)

    if y >= H - 3:
        if rng.random() < 0.45:
            return 144
        if rng.random() < 0.2:
            return 145
        return 143

    if (x + y + rng.randint(0, 2)) % 7 == 0 and y >= H - 5:
        return 143

    if rng.random() < 0.08 and y >= H - 6:
        return 145

    if y < 3 and rng.random() < 0.25:
        return 142

    if (x - y + rng.randint(0, 3)) % 5 == 0:
        return 141

    if rng.random() < 0.18:
        return 142

    return 140