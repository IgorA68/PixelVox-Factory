DEFAULT_W = 64
DEFAULT_D = 64
DEFAULT_H = 128
BLUEPRINT_DISPLAY_NAME = 'Rocket'
BLUEPRINT_DESCRIPTION = 'A stylized rocket assembled from a capsule body, cone nose, and a simple exhaust flare.'

from vox_art import engine as ev


BODY = 246
FIRE = 11
NOSE = 219

def make_model(x, y, z, W, D, H):
    cx, cy = W // 2, D // 2

    body_bottom = int(H * 0.15)
    body_top = int(H * 0.65)
    nose_height = int(H * 0.20)
    fire_radius = int(W * 0.1)
    body_radius = int(W * 0.15)

    if ev.is_sphere(x, y, z, cx, cy, cz=body_bottom, radius=fire_radius + 2):
        return FIRE

    if ev.is_capsule(x, y, z, cx, cy, body_bottom, body_top, radius=body_radius):
        return BODY

    if ev.is_cone(x, y, z, cx, cy, base_z=body_top, height=nose_height, radius=body_radius):
        return NOSE
        
    return 0