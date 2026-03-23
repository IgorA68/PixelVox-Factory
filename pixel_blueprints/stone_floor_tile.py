DEFAULT_W = 16
DEFAULT_H = 16
BLUEPRINT_DISPLAY_NAME = 'Stone Floor Tile'
BLUEPRINT_DESCRIPTION = 'A seeded stone floor tile with simple block seams and tonal variation for dungeon or ruin prototype maps.'

import random


BLUEPRINT_PALETTE_OVERRIDES = {
    170: (142, 144, 152),
    171: (174, 176, 184),
    172: (112, 114, 121),
    173: (82, 84, 92),
    174: (201, 194, 170),
}


def make_image(x, y, W, H, seed=None):
    tile_seed = 0 if seed is None else seed
    local_rng = random.Random(tile_seed * 3571 + x * 67 + y * 19)

    vertical_joint = x in (5, 10)
    horizontal_joint = y in (5, 10)
    chipped = (x, y) in ((5, 5), (10, 10), (10, 5), (5, 10)) and local_rng.random() < 0.5

    if chipped:
        return 174

    if vertical_joint or horizontal_joint:
        return 173

    block_index = ((0 if x < 5 else 1 if x < 10 else 2) + (0 if y < 5 else 1 if y < 10 else 2)) % 3
    noise_roll = local_rng.random()

    if block_index == 0:
        if noise_roll < 0.12:
            return 171
        if noise_roll < 0.24:
            return 172
        return 170

    if block_index == 1:
        if noise_roll < 0.15:
            return 174
        if noise_roll < 0.32:
            return 170
        return 171

    if noise_roll < 0.18:
        return 170
    if noise_roll < 0.36:
        return 171
    return 172