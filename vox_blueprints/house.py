DEFAULT_W = 64
DEFAULT_D = 64
DEFAULT_H = 64
BLUEPRINT_DISPLAY_NAME = 'House'
BLUEPRINT_DESCRIPTION = 'A simple house example that demonstrates box walls, cut-out openings, and a cone roof.'

from vox_art import engine as ev


WALL = 45
ROOF = 219

def make_model(x, y, z, W, D, H):
    cx, cy = W // 2, D // 2

    house_w = int(W * 0.6)
    house_d = int(D * 0.6)
    h_walls = int(H * 0.4)
    
    x0, x1 = cx - house_w//2, cx + house_w//2
    y0, y1 = cy - house_d//2, cy + house_d//2
    
    if ev.is_box(x, y, z, x0, y0, 0, x1, y1, h_walls):
        if (cx - 5 <= x <= cx + 5) and (y1 - 2 <= y <= y1 + 1) and (z <= h_walls * 0.7):
            return 0
        if (x0 - 1 <= x <= x0 + 1) and (cy - 4 <= y <= cy + 4) and (h_walls*0.4 <= z <= h_walls*0.7):
            return 0
            
        return WALL

    roof_start = h_walls
    roof_height = int(H * 0.3)
    if ev.is_cone(x, y, z, cx, cy, roof_start, roof_height, radius=int(house_w * 0.8)):
        return ROOF

    return 0