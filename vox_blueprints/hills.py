DEFAULT_W = 256
DEFAULT_D = 256
DEFAULT_H = 64
BLUEPRINT_DISPLAY_NAME = 'Hills'
BLUEPRINT_DESCRIPTION = 'Procedural rolling terrain built from layered sine and cosine waves.'

from vox_art import engine as ev
import math

def make_model(x, y, z, W, D, H):
    scale = 20.0
    height_map = (math.sin(x / scale) + math.cos(y / scale)) 
    
    ground_level = int((H / 4) + (height_map * (H / 8)))
    
    if z <= ground_level:
        if z == ground_level:
            if (x + y) % 5 == 0:
                return 75
            if (x * y) % 7 == 0:
                return 73
            return 74
        elif z > ground_level - 3:
            return 34
        else:
            return 252
            
    water_level = int(H / 5)
    if z <= water_level:
        return 105

    return 0