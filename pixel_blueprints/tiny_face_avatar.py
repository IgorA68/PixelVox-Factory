DEFAULT_W = 24
DEFAULT_H = 24
BLUEPRINT_DISPLAY_NAME = 'Tiny Face Avatar'
BLUEPRINT_DESCRIPTION = 'A tiny front-facing avatar with seeded hair variation and simple readable facial features for dialogue or NPC placeholders.'

import random

from pixel_art import engine as ep
from pixel_art.palettes import AVATAR_PALETTE


BLUEPRINT_PALETTE_OVERRIDES = AVATAR_PALETTE


def make_image(x, y, W, H, seed=None):
    cx = W // 2
    rng = random.Random(0 if seed is None else seed)
    hair_dark = 162
    hair_mid = 163
    shirt = 168
    accent = 167 if rng.randint(0, 1) == 0 else 166
    fringe_shift = rng.randint(-1, 1)
    eye_shift = rng.randint(0, 1)

    head_outer = ep.is_ellipse(x, y, cx, 10, 6, 7)
    head_inner = ep.is_ellipse(x, y, cx, 10, 5, 6)
    hair_cap = ep.is_ellipse(x, y, cx, 8, 7, 5)
    shirt_block = ep.is_rect(x, y, 7, 17, 16, 22)

    if shirt_block:
        if y == 17 and 10 <= x <= 13:
            return accent
        return shirt

    if hair_cap and y <= 11 + fringe_shift:
        if y <= 5 or x <= cx - 5 or x >= cx + 5:
            return hair_dark
        return hair_mid

    if head_outer and not head_inner:
        return 161

    if head_outer:
        if y == 10 and x in (10 - eye_shift, 14 + eye_shift):
            return 164
        if y == 10 and x in (9 - eye_shift, 15 + eye_shift):
            return 165
        if y == 13 and x == cx:
            return 166
        if y == 15 and cx - 2 <= x <= cx + 2:
            return 166
        if y <= 8 and abs(x - cx) <= 2:
            return 165
        return 160

    return 0