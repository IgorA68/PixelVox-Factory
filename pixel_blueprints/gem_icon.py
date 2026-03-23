DEFAULT_W = 16
DEFAULT_H = 16
BLUEPRINT_DISPLAY_NAME = 'Gem Icon'
BLUEPRINT_DESCRIPTION = 'A small palette-based gem icon with a seeded sparkle offset and transparent background.'

import random

from pixel_art import engine as ep
from pixel_art.palettes import GEM_PALETTE


BLUEPRINT_PALETTE_OVERRIDES = GEM_PALETTE


def make_image(x, y, W, H, seed=None):
    cx = W // 2
    cy = H // 2
    radius_x = max(3, W // 4)
    radius_y = max(4, H // 3)

    if not ep.is_diamond(x, y, cx, cy, radius_x, radius_y):
        return 0

    inner = ep.is_diamond(x, y, cx, cy, max(1, radius_x - 1), max(1, radius_y - 1))
    if not inner:
        return 123

    rng = random.Random(0 if seed is None else seed)
    sparkle_x = cx - 1 + rng.randint(-1, 1)
    sparkle_y = cy - 2 + rng.randint(-1, 0)
    shadow_line = cy + 1 + rng.randint(0, 1)

    if x == sparkle_x and y == sparkle_y:
        return 121

    if x <= cx and y <= cy:
        return 121

    if y >= shadow_line or x >= cx + 2:
        return 122

    return 120