DEFAULT_W = 64
DEFAULT_D = 64
DEFAULT_H = 64
BLUEPRINT_DISPLAY_NAME = 'My Blueprint'
BLUEPRINT_DESCRIPTION = 'Short summary of what this blueprint generates.'
BLUEPRINT_PALETTE_OVERRIDES = {
    120: (180, 150, 110),
    49: (180, 80, 65),
}

from vox_art import engine as ev


def make_model(x, y, z, W, D, H):
    cx, cy = W // 2, D // 2

    if ev.is_box(x, y, z, cx - 8, cy - 8, 0, cx + 8, cy + 8, 12):
        return 150

    if ev.is_cone(x, y, z, cx, cy, base_z=12, height=10, radius=10):
        return 49

    return 0