DEFAULT_W = 72
DEFAULT_D = 72
DEFAULT_H = 72
BLUEPRINT_DISPLAY_NAME = 'Primitive Layers'
BLUEPRINT_DESCRIPTION = 'A technique-focused example that shows how boxes, cylinders, cones, and spheres can be layered into one readable voxel form.'

from vox_art import engine as ev


BASE = 131
COLUMN = 250
ACCENT = 208
TOP = 221


def make_model(x, y, z, W, D, H):
    cx, cy = W // 2, D // 2

    pedestal_z1 = int(H * 0.16)
    body_z0 = pedestal_z1 + 1
    body_z1 = int(H * 0.56)
    collar_z0 = body_z1 - 4
    collar_z1 = body_z1 + 3
    cone_base_z = collar_z1 - 1
    cone_height = max(10, int(H * 0.17))
    top_z = cone_base_z + cone_height

    if ev.is_box(x, y, z, cx - 18, cy - 18, 0, cx + 18, cy + 18, pedestal_z1):
        trim_band = z == pedestal_z1 or abs(x - cx) == 18 or abs(y - cy) == 18
        return COLUMN if trim_band else BASE

    if ev.is_cylinder(x, y, z, cx, cy, 12, body_z0, body_z1):
        rib = (abs(x - cx) <= 1 or abs(y - cy) <= 1) and z >= body_z0 + 4
        return COLUMN if rib else BASE

    if ev.is_box(x, y, z, cx - 15, cy - 15, collar_z0, cx + 15, cy + 15, collar_z1):
        return ACCENT

    if ev.is_cone(x, y, z, cx, cy, base_z=cone_base_z, height=cone_height, radius=14):
        return COLUMN

    if ev.is_sphere(x, y, z, cx, cy, top_z + 2, radius=5):
        return TOP

    return 0