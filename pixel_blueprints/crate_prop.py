DEFAULT_W = 16
DEFAULT_H = 16
BLUEPRINT_DISPLAY_NAME = 'Crate Prop'
BLUEPRINT_DESCRIPTION = 'A small wooden crate prop with metal braces and a grounded shadow for side-view platformer or top-down prototyping.'

from pixel_art import engine as ep
from pixel_art.palettes import WOOD_PALETTE


BLUEPRINT_PALETTE_OVERRIDES = WOOD_PALETTE


def make_image(x, y, W, H):
    shadow = ep.is_rect(x, y, 3, H - 2, W - 4, H - 2)
    crate_outer = ep.is_rect(x, y, 3, 3, W - 4, H - 4)
    crate_inner = ep.is_rect(x, y, 4, 4, W - 5, H - 5)

    if shadow and not crate_outer:
        return 155

    if not crate_outer:
        return 0

    if not crate_inner:
        return 152

    vertical_brace = x in (5, W - 6)
    horizontal_brace = y in (5, H - 6)
    cross_beam = abs((x - 4) - (y - 4)) <= 1 or abs((x - 4) + (y - 4) - 14) <= 1
    bolt = (x, y) in ((5, 5), (W - 6, 5), (5, H - 6), (W - 6, H - 6))

    if bolt:
        return 154

    if vertical_brace or horizontal_brace:
        return 153

    if cross_beam:
        return 151

    if y >= H - 6 or x >= W - 7:
        return 150

    return 151