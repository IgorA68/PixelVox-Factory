DEFAULT_W = 96
DEFAULT_D = 96
DEFAULT_H = 160
BLUEPRINT_DISPLAY_NAME = 'Tower'
BLUEPRINT_DESCRIPTION = 'A layered stone tower with a raised plinth, balcony ring, battlements, and a tall spire.'

import math

from vox_art import engine as ev


STONE_DARK = 252
STONE_MID = 249
STONE_LIGHT = 247
ROOF_DARK = 129
ROOF_LIGHT = 128
WINDOW_GLOW = 151
DOOR_COLOR = 59


def _dist_xy(x, y, cx, cy):
    return math.hypot(x - cx, y - cy)


def _stone_color(x, y, z):
    noise = math.sin(x * 0.31) + math.cos(y * 0.27) + math.sin(z * 0.19)
    if noise > 1.1:
        return STONE_LIGHT
    if noise < -0.7:
        return STONE_DARK
    return STONE_MID


def _roof_color(x, y, z):
    return ROOF_LIGHT if (x + y + z) % 5 == 0 else ROOF_DARK


def make_model(x, y, z, W, D, H):
    cx, cy = W // 2, D // 2

    plinth_half = int(W * 0.31)
    plinth_height = int(H * 0.12)
    shaft_radius = max(8, int(W * 0.17))
    shaft_bottom = plinth_height - 1
    shaft_top = int(H * 0.72)
    balcony_z = int(H * 0.58)
    balcony_outer = shaft_radius + max(4, int(W * 0.05))
    parapet_z0 = shaft_top - max(4, int(H * 0.035))
    roof_base_z = shaft_top - 2
    roof_height = int(H * 0.2)
    roof_radius = shaft_radius + max(4, int(W * 0.05))
    lantern_base = roof_base_z + roof_height - max(7, int(H * 0.04))
    lantern_top = lantern_base + max(6, int(H * 0.045))
    lantern_radius = max(2, int(W * 0.045))
    spire_height = max(10, int(H * 0.12))

    dist = _dist_xy(x, y, cx, cy)

    if ev.is_box(x, y, z, cx - plinth_half, cy - plinth_half, 0, cx + plinth_half, cy + plinth_half, plinth_height):
        if abs(x - cx) <= 4 and y >= cy + plinth_half - 2 and z <= int(plinth_height * 0.72):
            return DOOR_COLOR
        return _stone_color(x, y, z)

    if ev.is_cylinder(x, y, z, cx, cy, shaft_radius, shaft_bottom, shaft_top):
        if z <= plinth_height + 10 and abs(x - cx) <= 3 and y >= cy + shaft_radius - 1:
            return 0

        for window_z in (int(H * 0.23), int(H * 0.38), int(H * 0.53)):
            if window_z <= z <= window_z + 5:
                if abs(x - cx) <= 1 and abs(y - (cy + shaft_radius - 1)) <= 1:
                    return WINDOW_GLOW
                if abs(y - cy) <= 1 and abs(x - (cx - shaft_radius + 1)) <= 1:
                    return WINDOW_GLOW

        return _stone_color(x, y, z)

    if balcony_z - 2 <= z <= balcony_z + 2 and shaft_radius + 1 <= dist <= balcony_outer:
        return _stone_color(x, y, z)

    if ev.is_torus(x, y, z, cx, cy, balcony_z - 4, balcony_outer - 1, 2.2):
        return _stone_color(x, y, z)

    if parapet_z0 <= z <= shaft_top + 2 and shaft_radius - 1 <= dist <= balcony_outer - 1:
        angle = (math.atan2(y - cy, x - cx) + math.tau) % math.tau
        merlon_index = int(angle / (math.tau / 12.0))
        if merlon_index % 2 == 0:
            return _stone_color(x, y, z)

    for support_angle in (0.25, 1.85, 3.45, 5.05):
        support_x = cx + int(math.cos(support_angle) * (balcony_outer - 2))
        support_y = cy + int(math.sin(support_angle) * (balcony_outer - 2))
        if ev.is_box(x, y, z, support_x - 1, support_y - 1, plinth_height, support_x + 1, support_y + 1, balcony_z - 1):
            return _stone_color(x, y, z)

    if ev.is_cone(x, y, z, cx, cy, roof_base_z, roof_height, roof_radius):
        return _roof_color(x, y, z)

    if ev.is_cylinder(x, y, z, cx, cy, lantern_radius, lantern_base, lantern_top):
        if z in (lantern_base + 1, lantern_top - 1) or dist >= lantern_radius - 0.5:
            return STONE_LIGHT
        return WINDOW_GLOW

    if ev.is_cone(x, y, z, cx, cy, lantern_top, spire_height, lantern_radius + 1):
        return ROOF_LIGHT

    return 0


if __name__ == '__main__':
    ev.save_as_vox('tower', DEFAULT_W, DEFAULT_D, DEFAULT_H, make_model)