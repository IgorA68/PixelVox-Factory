DEFAULT_W = 16
DEFAULT_H = 16
BLUEPRINT_DISPLAY_NAME = 'Potion Icon'
BLUEPRINT_DESCRIPTION = 'A tiny potion bottle icon with seeded liquid tint and a readable silhouette for inventory-style UI.'

import random

from pixel_art import engine as ep
from pixel_art.palettes import POTION_PALETTE


BLUEPRINT_PALETTE_OVERRIDES = POTION_PALETTE


def make_image(x, y, W, H, seed=None):
    cx = W // 2
    neck_top = 1
    neck_bottom = 4
    body_top = 4
    body_bottom = H - 3

    rng = random.Random(0 if seed is None else seed)
    liquid_main = 133 if rng.randint(0, 1) == 0 else 134
    liquid_shadow = 135 if liquid_main == 133 else 133
    bubble_x = cx + rng.randint(-2, 1)
    bubble_y = body_top + 3 + rng.randint(0, 2)

    neck_outer = ep.is_rect(x, y, cx - 1, neck_top, cx + 1, neck_bottom)
    neck_inner = ep.is_rect(x, y, cx, neck_top + 1, cx, neck_bottom - 1)
    body_outer = ep.is_ellipse(x, y, cx, (body_top + body_bottom) // 2, 4, 5)
    body_inner = ep.is_ellipse(x, y, cx, (body_top + body_bottom) // 2, 3, 4)
    cork = ep.is_rect(x, y, cx - 1, 0, cx + 1, 1)

    if cork:
        return 136

    if neck_outer and not neck_inner:
        return 132

    if body_outer and not body_inner:
        return 132

    if neck_outer or body_outer:
        liquid_surface = body_top + 3

        if y >= liquid_surface:
            if (x, y) == (bubble_x, bubble_y):
                return 134
            if x >= cx + 1 or y >= body_bottom - 1:
                return liquid_shadow
            return liquid_main

        if x <= cx - 1 and y <= body_top + 2:
            return 130
        return 131

    return 0