import math


def validate_real_number(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f'{name} must be a real number, got {value!r}')


def validate_non_negative_measure(name, value):
    validate_real_number(name, value)
    if value < 0:
        raise ValueError(f'{name} must be non-negative, got {value!r}')


def validate_positive_measure(name, value):
    validate_real_number(name, value)
    if value <= 0:
        raise ValueError(f'{name} must be greater than zero, got {value!r}')


def is_sphere(x, y, z, cx, cy, cz, radius):
    validate_non_negative_measure('radius', radius)
    return (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2 <= radius ** 2


def is_cylinder(x, y, z, cx, cy, r, z_min, z_max):
    validate_non_negative_measure('r', r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2 and z_min <= z <= z_max


def is_cone(x, y, z, cx, cy, base_z, height, radius):
    validate_positive_measure('height', height)
    validate_non_negative_measure('radius', radius)

    if not (base_z <= z <= base_z + height):
        return False

    current_radius = radius * (1 - (z - base_z) / height)
    return (x - cx) ** 2 + (y - cy) ** 2 <= current_radius ** 2


def is_capsule(x, y, z, cx, cy, z_min, z_max, radius):
    validate_non_negative_measure('radius', radius)
    if z_min <= z <= z_max:
        return (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2
    if z < z_min:
        return (x - cx) ** 2 + (y - cy) ** 2 + (z - z_min) ** 2 <= radius ** 2
    return (x - cx) ** 2 + (y - cy) ** 2 + (z - z_max) ** 2 <= radius ** 2


def is_torus(x, y, z, cx, cy, cz, main_radius, tube_radius):
    validate_non_negative_measure('main_radius', main_radius)
    validate_non_negative_measure('tube_radius', tube_radius)

    distance_to_axis = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    return (main_radius - distance_to_axis) ** 2 + (z - cz) ** 2 <= tube_radius ** 2


def is_box(x, y, z, x0, y0, z0, x1, y1, z1):
    return x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1
