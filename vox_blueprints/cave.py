DEFAULT_W = 160
DEFAULT_D = 160
DEFAULT_H = 96
BLUEPRINT_DISPLAY_NAME = 'Cave'
BLUEPRINT_DESCRIPTION = 'A layered cave volume with carved chambers, tunnel voids, and simple stalagmites for interior structure.'

import math


STONE_DARK = 253
STONE_MID = 251
STONE_LIGHT = 248
MOSS_DARK = 167
MOSS_LIGHT = 124
WATER = 157


def _dist3(x, y, z, cx, cy, cz):
    dx = x - cx
    dy = y - cy
    dz = z - cz
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def _inside_ellipsoid(x, y, z, cx, cy, cz, rx, ry, rz):
    if rx <= 0 or ry <= 0 or rz <= 0:
        return False

    dx = (x - cx) / rx
    dy = (y - cy) / ry
    dz = (z - cz) / rz
    return dx * dx + dy * dy + dz * dz <= 1.0


def _rock_color(x, y, z, ceiling, floor_level):
    damp_band = z <= floor_level + 2
    moss_noise = math.sin(x * 0.16) + math.cos(y * 0.14) + math.sin(z * 0.23)
    if damp_band and moss_noise > 0.5:
        return MOSS_LIGHT
    if damp_band and moss_noise > -0.2:
        return MOSS_DARK

    shade = math.sin(x * 0.19) + math.cos(y * 0.21) + math.sin((ceiling - z) * 0.17)
    if shade > 1.0:
        return STONE_LIGHT
    if shade < -0.8:
        return STONE_DARK
    return STONE_MID


def make_model(x, y, z, W, D, H):
    cx, cy = W / 2.0, D / 2.0
    wall_margin = max(10, int(min(W, D) * 0.08))

    floor_wave = math.sin(x * 0.08) * 3.2 + math.cos(y * 0.07) * 2.7 + math.sin((x + y) * 0.03) * 2.0
    floor_level = int(H * 0.18 + floor_wave)

    ceiling_wave = math.sin(x * 0.05 + 0.9) * 5.5 + math.cos(y * 0.06 - 0.4) * 4.5 + math.sin((x - y) * 0.025) * 4.0
    ceiling = int(H * 0.76 + ceiling_wave)

    if x < wall_margin or x >= W - wall_margin or y < wall_margin or y >= D - wall_margin:
        return STONE_DARK

    if z > ceiling or z < 0:
        return 0

    if z <= floor_level:
        if z <= floor_level - 3:
            return WATER if z <= int(H * 0.11) else _rock_color(x, y, z, ceiling, floor_level)
        return _rock_color(x, y, z, ceiling, floor_level)

    chamber_main = _inside_ellipsoid(x, y, z, cx, cy, H * 0.42, W * 0.24, D * 0.22, H * 0.2)
    chamber_side = _inside_ellipsoid(x, y, z, cx - W * 0.17, cy + D * 0.08, H * 0.38, W * 0.16, D * 0.14, H * 0.14)
    chamber_high = _inside_ellipsoid(x, y, z, cx + W * 0.14, cy - D * 0.12, H * 0.54, W * 0.13, D * 0.12, H * 0.12)

    tunnel_1 = _inside_ellipsoid(x, y, z, cx - W * 0.02, cy + D * 0.02, H * 0.32, W * 0.28, D * 0.08, H * 0.08)
    tunnel_2 = _inside_ellipsoid(x, y, z, cx + W * 0.1, cy - D * 0.08, H * 0.48, W * 0.18, D * 0.07, H * 0.07)
    skylight = _inside_ellipsoid(x, y, z, cx + W * 0.12, cy - D * 0.14, H * 0.72, W * 0.06, D * 0.06, H * 0.2)

    if chamber_main or chamber_side or chamber_high or tunnel_1 or tunnel_2 or skylight:
        return 0

    for spike_x, spike_y, spike_height, spike_radius in (
        (cx - W * 0.1, cy + D * 0.04, H * 0.16, W * 0.05),
        (cx + W * 0.03, cy - D * 0.09, H * 0.12, W * 0.04),
        (cx + W * 0.16, cy + D * 0.12, H * 0.14, W * 0.045),
    ):
        spike_base = floor_level - 1
        if z < spike_base or z > spike_base + spike_height:
            continue

        progress = (z - spike_base) / max(1.0, spike_height)
        current_radius = spike_radius * (1.0 - progress)
        if current_radius <= 0:
            continue

        if math.hypot(x - spike_x, y - spike_y) <= current_radius:
            return _rock_color(x, y, z, ceiling, floor_level)

    return _rock_color(x, y, z, ceiling, floor_level)


if __name__ == '__main__':
    from vox_art import engine as ev

    ev.save_as_vox('cave', DEFAULT_W, DEFAULT_D, DEFAULT_H, make_model)