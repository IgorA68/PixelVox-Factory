DEFAULT_W = 80
DEFAULT_D = 64
DEFAULT_H = 72
BLUEPRINT_DISPLAY_NAME = 'Negative Space Arch'
BLUEPRINT_DESCRIPTION = 'A technique-focused example that demonstrates carving silhouette and interior space out of a larger mass.'

from vox_art import engine as ev


STONE = 246
TRIM = 252
ACCENT = 208


def make_model(x, y, z, W, D, H):
    cx, cy = W // 2, D // 2

    outer_x0 = cx - 26
    outer_x1 = cx + 26
    outer_y0 = cy - 12
    outer_y1 = cy + 12
    outer_z0 = 0
    outer_z1 = int(H * 0.72)

    if not ev.is_box(x, y, z, outer_x0, outer_y0, outer_z0, outer_x1, outer_y1, outer_z1):
        return 0

    inside_arch = ev.is_cylinder(x, y, z, cx, cy, 10, 0, int(H * 0.48)) and z <= int(H * 0.38)
    inner_hall = ev.is_box(x, y, z, cx - 20, cy - 8, 0, cx + 20, cy + 8, int(H * 0.34))
    skylight = ev.is_box(x, y, z, cx - 6, cy - 4, int(H * 0.46), cx + 6, cy + 4, int(H * 0.62))

    if inside_arch or inner_hall or skylight:
        return 0

    edge_trim = x in (outer_x0, outer_x1) or y in (outer_y0, outer_y1)
    crown_band = z >= outer_z1 - 3
    center_accent = abs(x - cx) <= 2 and z >= int(H * 0.50) and z <= int(H * 0.64) and abs(y - cy) <= 10

    if center_accent:
        return ACCENT
    if edge_trim or crown_band:
        return TRIM
    return STONE