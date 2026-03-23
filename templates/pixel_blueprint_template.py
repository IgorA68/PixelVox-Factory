DEFAULT_W = 16
DEFAULT_H = 16
BLUEPRINT_DISPLAY_NAME = 'My Pixel Blueprint'
BLUEPRINT_DESCRIPTION = 'Short summary of what this pixel blueprint generates.'
BLUEPRINT_PALETTE_OVERRIDES = {
    120: (86, 180, 255),
    121: (188, 235, 255),
    122: (35, 96, 189),
}

from pixel_art import engine as ep


def make_image(x, y, W, H):
    cx = W // 2
    cy = H // 2

    if ep.is_diamond(x, y, cx, cy, max(2, W // 4), max(2, H // 4)):
        if ep.is_diamond_outline(x, y, cx, cy, max(2, W // 4), max(2, H // 4)):
            return 122

        if x <= cx and y <= cy:
            return 121

        return 120

    return 0