DEFAULT_W = 96
DEFAULT_D = 96
DEFAULT_H = 112
BLUEPRINT_DISPLAY_NAME = 'Sci-Fi Prop'
BLUEPRINT_DESCRIPTION = 'A hard-surface reactor prop with a raised platform, glowing core, energy ring, and side modules.'

import math

from vox_art import engine as ev


METAL_DARK = 250
METAL_MID = 252
METAL_LIGHT = 254
PANEL_DARK = 131
PANEL_LIGHT = 133
GLOW_CORE = 106
GLOW_HOT = 221


def _radial_distance(x, y, cx, cy):
    return math.hypot(x - cx, y - cy)


def _metal_color(x, y, z):
    noise = math.sin(x * 0.27) + math.cos(y * 0.22) + math.sin(z * 0.18)
    if noise > 1.0:
        return METAL_LIGHT
    if noise < -0.85:
        return METAL_DARK
    return METAL_MID


def _panel_color(x, y, z):
    return PANEL_LIGHT if (x + y + z) % 6 < 2 else PANEL_DARK


def make_model(x, y, z, W, D, H):
    cx, cy = W // 2, D // 2

    base_half = int(W * 0.28)
    base_height = int(H * 0.11)
    plinth_half = int(W * 0.2)
    plinth_height = int(H * 0.18)
    core_radius = max(6, int(W * 0.09))
    core_bottom = plinth_height
    core_top = int(H * 0.74)
    shell_radius = core_radius + max(4, int(W * 0.05))
    shell_bottom = int(H * 0.2)
    shell_top = int(H * 0.64)
    ring_z = int(H * 0.48)
    ring_main_radius = int(W * 0.2)
    ring_tube_radius = max(3, int(W * 0.04))
    fin_height = int(H * 0.24)
    cap_bottom = shell_top
    cap_height = int(H * 0.16)

    if ev.is_box(x, y, z, cx - base_half, cy - base_half, 0, cx + base_half, cy + base_half, base_height):
        edge_band = abs(abs(x - cx) - base_half) <= 1 or abs(abs(y - cy) - base_half) <= 1
        return _panel_color(x, y, z) if edge_band else _metal_color(x, y, z)

    if ev.is_box(x, y, z, cx - plinth_half, cy - plinth_half, base_height, cx + plinth_half, cy + plinth_half, plinth_height):
        if abs(x - cx) <= 5 and y >= cy + plinth_half - 1 and z <= base_height + 6:
            return 0
        return _metal_color(x, y, z)

    if ev.is_capsule(x, y, z, cx, cy, core_bottom, core_top, core_radius):
        if z >= shell_bottom and z <= shell_top and _radial_distance(x, y, cx, cy) >= core_radius - 1:
            return GLOW_HOT if (z + x + y) % 5 == 0 else GLOW_CORE
        return GLOW_CORE

    if ev.is_cylinder(x, y, z, cx, cy, shell_radius, shell_bottom, shell_top):
        if _radial_distance(x, y, cx, cy) < shell_radius - 2:
            return 0
        window_band = ring_z - 5 <= z <= ring_z + 5
        if window_band and abs(x - cx) <= 2:
            return GLOW_HOT
        if window_band and abs(y - cy) <= 2:
            return GLOW_HOT
        return _metal_color(x, y, z)

    if ev.is_torus(x, y, z, cx, cy, ring_z, ring_main_radius, ring_tube_radius):
        return GLOW_HOT if (x + y + z) % 4 == 0 else PANEL_LIGHT

    for pod_dx, pod_dy in ((ring_main_radius + 6, 0), (-ring_main_radius - 6, 0), (0, ring_main_radius + 6), (0, -ring_main_radius - 6)):
        pod_cx = cx + pod_dx
        pod_cy = cy + pod_dy
        if ev.is_capsule(x, y, z, pod_cx, pod_cy, int(H * 0.3), int(H * 0.55), max(4, int(W * 0.05))):
            if abs(z - int(H * 0.42)) <= 2:
                return PANEL_LIGHT
            return _panel_color(x, y, z)

    for fin_dx, fin_dy, fin_w, fin_d in (
        (0, ring_main_radius + 2, 2, 8),
        (0, -ring_main_radius - 2, 2, 8),
        (ring_main_radius + 2, 0, 8, 2),
        (-ring_main_radius - 2, 0, 8, 2),
    ):
        if ev.is_box(
            x,
            y,
            z,
            cx + fin_dx - fin_w,
            cy + fin_dy - fin_d,
            base_height,
            cx + fin_dx + fin_w,
            cy + fin_dy + fin_d,
            base_height + fin_height,
        ):
            fin_progress = (z - base_height) / max(1, fin_height)
            limit = (1.0 - fin_progress) * max(fin_w, fin_d)
            local_x = abs(x - (cx + fin_dx))
            local_y = abs(y - (cy + fin_dy))
            if max(local_x, local_y) <= max(1, int(limit)):
                return _panel_color(x, y, z)

    if ev.is_cone(x, y, z, cx, cy, cap_bottom, cap_height, shell_radius - 1):
        return _panel_color(x, y, z)

    if ev.is_box(x, y, z, cx - 2, cy - 2, cap_bottom + cap_height, cx + 2, cy + 2, H - 8):
        return METAL_LIGHT

    if ev.is_sphere(x, y, z, cx, cy, H - 8, 4):
        return GLOW_HOT

    return 0


if __name__ == '__main__':
    ev.save_as_vox('sci_fi_prop', DEFAULT_W, DEFAULT_D, DEFAULT_H, make_model)