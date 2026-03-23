DEFAULT_W = 112
DEFAULT_D = 80
DEFAULT_H = 64
BLUEPRINT_DISPLAY_NAME = 'Vehicle'
BLUEPRINT_DESCRIPTION = 'A compact rover-style vehicle with a layered chassis, wheel arches, cockpit canopy, and rear module.'

from vox_art import engine as ev


BODY_DARK = 88
BODY_MID = 45
BODY_LIGHT = 46
FRAME_DARK = 253
FRAME_LIGHT = 249
WINDOW = 152
ACCENT = 11
TIRE = 255
HEADLIGHT = 2
TAILLIGHT = 218


def _body_color(x, y, z):
    return BODY_LIGHT if (x + z) % 7 < 2 else BODY_MID


def _frame_color(x, y, z):
    return FRAME_LIGHT if (x + y + z) % 6 == 0 else FRAME_DARK


def _inside_wheel(x, y, z, wheel_x, wheel_y, wheel_z, radius, half_thickness):
    if abs(y - wheel_y) > half_thickness:
        return False

    dx = x - wheel_x
    dz = z - wheel_z
    return dx * dx + dz * dz <= radius * radius


def _wheel_distance_sq(x, z, wheel_x, wheel_z):
    dx = x - wheel_x
    dz = z - wheel_z
    return dx * dx + dz * dz


def make_model(x, y, z, W, D, H):
    cx, cy = W // 2, D // 2

    chassis_x0 = cx - int(W * 0.28)
    chassis_x1 = cx + int(W * 0.22)
    chassis_y0 = cy - int(D * 0.22)
    chassis_y1 = cy + int(D * 0.22)
    chassis_z0 = int(H * 0.16)
    chassis_z1 = int(H * 0.34)

    deck_x0 = cx - int(W * 0.18)
    deck_x1 = cx + int(W * 0.08)
    deck_y0 = cy - int(D * 0.18)
    deck_y1 = cy + int(D * 0.18)
    deck_z0 = chassis_z1 + 1
    deck_z1 = int(H * 0.44)

    cabin_x0 = cx - int(W * 0.08)
    cabin_x1 = cx + int(W * 0.16)
    cabin_y0 = cy - int(D * 0.16)
    cabin_y1 = cy + int(D * 0.16)
    cabin_z0 = deck_z0
    cabin_z1 = int(H * 0.56)

    rear_x0 = cx - int(W * 0.36)
    rear_x1 = cx - int(W * 0.2)
    rear_y0 = cy - int(D * 0.16)
    rear_y1 = cy + int(D * 0.16)
    rear_z0 = chassis_z1 - 1
    rear_z1 = int(H * 0.46)

    wheel_radius = max(5, int(H * 0.12))
    wheel_z = wheel_radius
    wheel_half_thickness = max(2, int(D * 0.035))
    wheel_x_positions = (cx - int(W * 0.22), cx + int(W * 0.14))
    wheel_y_positions = (cy - int(D * 0.27), cy + int(D * 0.27))
    wheel_inner_radius = max(2, wheel_radius - 3)
    wheel_hub_radius = max(1, wheel_radius - 5)

    for wheel_x in wheel_x_positions:
        strut_z0 = wheel_z + wheel_radius - 2
        strut_z1 = chassis_z0 + 4
        if ev.is_box(x, y, z, wheel_x - 1, cy - 1, strut_z0, wheel_x + 1, cy + 1, strut_z1):
            return FRAME_DARK

    front_bumper = ev.is_box(x, y, z, chassis_x1 + 1, cy - 6, chassis_z0 + 2, chassis_x1 + 4, cy + 6, chassis_z0 + 6)
    if front_bumper:
        headlight_band = abs(y - cy) >= 3 and z >= chassis_z0 + 4
        return HEADLIGHT if headlight_band else FRAME_LIGHT

    if ev.is_box(x, y, z, rear_x0 - 2, cy - 5, chassis_z0 + 3, rear_x0, cy + 5, chassis_z0 + 7):
        tail_light_band = x <= rear_x0 - 1 and abs(y - cy) >= 2 and z >= chassis_z0 + 5
        return TAILLIGHT if tail_light_band else FRAME_DARK

    if ev.is_box(x, y, z, cabin_x0 + 1, cy - 1, cabin_z1 + 2, cabin_x1 - 2, cy + 1, cabin_z1 + 4):
        return FRAME_LIGHT

    if ev.is_box(x, y, z, cabin_x0 + 1, cy, cabin_z1 + 5, cabin_x0 + 2, cy, cabin_z1 + 9):
        return ACCENT

    for wheel_x in wheel_x_positions:
        for wheel_y in wheel_y_positions:
            if _inside_wheel(x, y, z, wheel_x, wheel_y, wheel_z, wheel_radius, wheel_half_thickness):
                distance_sq = _wheel_distance_sq(x, z, wheel_x, wheel_z)
                if _inside_wheel(x, y, z, wheel_x, wheel_y, wheel_z, wheel_inner_radius, wheel_half_thickness - 1):
                    if distance_sq <= wheel_hub_radius * wheel_hub_radius:
                        return FRAME_LIGHT
                    if abs(x - wheel_x) <= 1 or abs(z - wheel_z) <= 1:
                        return FRAME_DARK
                    return FRAME_LIGHT
                return TIRE

    if ev.is_box(x, y, z, chassis_x0, chassis_y0, chassis_z0, chassis_x1, chassis_y1, chassis_z1):
        wheel_cutout = False
        for wheel_x in wheel_x_positions:
            for wheel_y in wheel_y_positions:
                arch_dx = x - wheel_x
                arch_dz = z - wheel_z
                arch_radius = wheel_radius + 2
                if abs(y - wheel_y) <= wheel_half_thickness + 2 and arch_dx * arch_dx + arch_dz * arch_dz <= arch_radius * arch_radius:
                    wheel_cutout = True
                    break
            if wheel_cutout:
                break

        if wheel_cutout:
            return 0

        side_stripe = x >= chassis_x0 + 6 and x <= chassis_x1 - 4 and z == chassis_z0 + 8 and abs(y - cy) >= int(D * 0.16)
        if side_stripe:
            return ACCENT

        side_band = y in (chassis_y0, chassis_y1)
        return _frame_color(x, y, z) if side_band else _body_color(x, y, z)

    if ev.is_box(x, y, z, deck_x0, deck_y0, deck_z0, deck_x1, deck_y1, deck_z1):
        service_hatch = x >= deck_x0 + 3 and x <= deck_x1 - 2 and abs(y - cy) <= 2 and z == deck_z1 - 1
        if service_hatch:
            return FRAME_LIGHT
        return _body_color(x, y, z)

    if ev.is_box(x, y, z, rear_x0, rear_y0, rear_z0, rear_x1, rear_y1, rear_z1):
        rear_panel = x == rear_x0 + 2 and abs(y - cy) <= 3 and z >= rear_z0 + 4 and z <= rear_z1 - 4
        if rear_panel:
            return ACCENT
        panel_band = x in (rear_x0, rear_x1) or y in (rear_y0, rear_y1)
        return _frame_color(x, y, z) if panel_band else BODY_DARK

    if ev.is_box(x, y, z, cabin_x0, cabin_y0, cabin_z0, cabin_x1, cabin_y1, cabin_z1):
        front_window = x >= cabin_x1 - 1 and cabin_z0 + 4 <= z <= cabin_z1 - 3 and abs(y - cy) <= int(D * 0.1)
        side_window = (y == cabin_y0 or y == cabin_y1) and cabin_z0 + 4 <= z <= cabin_z1 - 2 and x >= cabin_x0 + 2
        roof_trim = z == cabin_z1 - 1 and x >= cabin_x0 + 2 and x <= cabin_x1 - 2 and abs(y - cy) >= 3
        if roof_trim:
            return FRAME_LIGHT
        if front_window or side_window:
            return WINDOW
        return _body_color(x, y, z)

    for layer_index, (layer_x0, layer_x1, layer_y0, layer_y1, layer_z0, layer_z1) in enumerate((
        (cabin_x1 - 8, cabin_x1 + 1, cy - 9, cy + 9, cabin_z0 + 2, cabin_z0 + 5),
        (cabin_x1 - 5, cabin_x1 + 3, cy - 8, cy + 8, cabin_z0 + 6, cabin_z0 + 9),
        (cabin_x1 - 2, cabin_x1 + 4, cy - 7, cy + 7, cabin_z0 + 10, cabin_z0 + 12),
    )):
        if ev.is_box(x, y, z, layer_x0, layer_y0, layer_z0, layer_x1, layer_y1, layer_z1):
            if x >= layer_x1 - 1 and abs(y - cy) <= max(3, 8 - layer_index) and z < layer_z1:
                return WINDOW
            if y in (layer_y0, layer_y1) and x >= layer_x0 + 1:
                return WINDOW
            return BODY_LIGHT

    if ev.is_box(x, y, z, cabin_x0 - 3, cy - 1, cabin_z1 - 1, cabin_x1 + 2, cy + 1, cabin_z1 + 1):
        return FRAME_LIGHT

    if ev.is_box(x, y, z, cx - int(W * 0.06), cy - 1, chassis_z1 + 1, cx + int(W * 0.18), cy + 1, chassis_z1 + 3):
        return FRAME_LIGHT

    if ev.is_box(x, y, z, rear_x0 + 2, rear_y0 - 2, rear_z1 - 6, rear_x1 - 2, rear_y0, rear_z1 - 3):
        return ACCENT

    if ev.is_box(x, y, z, chassis_x0 - 3, cy - 2, chassis_z0 + 2, chassis_x0, cy + 2, chassis_z0 + 8):
        return ACCENT

    return 0


if __name__ == '__main__':
    ev.save_as_vox('vehicle', DEFAULT_W, DEFAULT_D, DEFAULT_H, make_model)