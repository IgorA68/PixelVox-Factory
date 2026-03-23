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
        raise ValueError(f'{name} must be positive, got {value!r}')


def _validate_vertices(name, vertices, minimum_points):
    if not isinstance(vertices, (list, tuple)):
        raise TypeError(f'{name} must be a list or tuple of (x, y) pairs, got {vertices!r}')
    if len(vertices) < minimum_points:
        raise ValueError(f'{name} must contain at least {minimum_points} points, got {len(vertices)}')

    normalized_vertices = []
    for index, vertex in enumerate(vertices):
        if not isinstance(vertex, (list, tuple)) or len(vertex) != 2:
            raise TypeError(f'{name}[{index}] must be a 2-item point, got {vertex!r}')

        point_x, point_y = vertex
        validate_real_number(f'{name}[{index}][0]', point_x)
        validate_real_number(f'{name}[{index}][1]', point_y)
        normalized_vertices.append((point_x, point_y))

    return normalized_vertices


def _distance_squared_to_segment(px, py, x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0

    if dx == 0 and dy == 0:
        return (px - x0) ** 2 + (py - y0) ** 2

    t = ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    nearest_x = x0 + t * dx
    nearest_y = y0 + t * dy
    return (px - nearest_x) ** 2 + (py - nearest_y) ** 2


def _point_on_segment(px, py, x0, y0, x1, y1):
    cross = (px - x0) * (y1 - y0) - (py - y0) * (x1 - x0)
    if abs(cross) > 1e-9:
        return False

    return min(x0, x1) <= px <= max(x0, x1) and min(y0, y1) <= py <= max(y0, y1)


def is_rect(x, y, x0, y0, x1, y1):
    return x0 <= x <= x1 and y0 <= y <= y1


def is_rect_outline(x, y, x0, y0, x1, y1, thickness=1):
    validate_positive_measure('thickness', thickness)

    if not is_rect(x, y, x0, y0, x1, y1):
        return False

    inner_x0 = x0 + thickness
    inner_y0 = y0 + thickness
    inner_x1 = x1 - thickness
    inner_y1 = y1 - thickness

    if inner_x0 > inner_x1 or inner_y0 > inner_y1:
        return True

    return not is_rect(x, y, inner_x0, inner_y0, inner_x1, inner_y1)


def is_line(x, y, x0, y0, x1, y1, thickness=1):
    validate_positive_measure('thickness', thickness)
    radius = thickness / 2.0
    return _distance_squared_to_segment(x, y, x0, y0, x1, y1) <= radius * radius


def is_polyline(x, y, vertices, thickness=1, closed=False):
    validate_positive_measure('thickness', thickness)
    if not isinstance(closed, bool):
        raise TypeError(f'closed must be a boolean, got {closed!r}')

    normalized_vertices = _validate_vertices('vertices', vertices, minimum_points=2)
    segment_count = len(normalized_vertices) if closed else len(normalized_vertices) - 1

    for index in range(segment_count):
        x0, y0 = normalized_vertices[index]
        x1, y1 = normalized_vertices[(index + 1) % len(normalized_vertices)]
        if is_line(x, y, x0, y0, x1, y1, thickness=thickness):
            return True

    return False


def is_circle(x, y, cx, cy, radius):
    validate_non_negative_measure('radius', radius)
    return (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2


def is_circle_outline(x, y, cx, cy, radius, thickness=1):
    validate_positive_measure('thickness', thickness)
    validate_non_negative_measure('radius', radius)

    if not is_circle(x, y, cx, cy, radius):
        return False

    inner_radius = radius - thickness
    if inner_radius < 0:
        return True

    return not is_circle(x, y, cx, cy, inner_radius)


def is_ellipse(x, y, cx, cy, radius_x, radius_y):
    validate_non_negative_measure('radius_x', radius_x)
    validate_non_negative_measure('radius_y', radius_y)

    if radius_x == 0 or radius_y == 0:
        return x == cx and y == cy

    dx = (x - cx) / radius_x
    dy = (y - cy) / radius_y
    return dx * dx + dy * dy <= 1.0


def is_ellipse_outline(x, y, cx, cy, radius_x, radius_y, thickness=1):
    validate_positive_measure('thickness', thickness)
    validate_non_negative_measure('radius_x', radius_x)
    validate_non_negative_measure('radius_y', radius_y)

    if not is_ellipse(x, y, cx, cy, radius_x, radius_y):
        return False

    inner_radius_x = radius_x - thickness
    inner_radius_y = radius_y - thickness
    if inner_radius_x < 0 or inner_radius_y < 0:
        return True

    return not is_ellipse(x, y, cx, cy, inner_radius_x, inner_radius_y)


def is_diamond(x, y, cx, cy, radius_x, radius_y):
    validate_non_negative_measure('radius_x', radius_x)
    validate_non_negative_measure('radius_y', radius_y)

    if radius_x == 0 or radius_y == 0:
        return x == cx and y == cy

    dx = abs(x - cx) / radius_x
    dy = abs(y - cy) / radius_y
    return dx + dy <= 1.0


def is_diamond_outline(x, y, cx, cy, radius_x, radius_y, thickness=1):
    validate_positive_measure('thickness', thickness)
    validate_non_negative_measure('radius_x', radius_x)
    validate_non_negative_measure('radius_y', radius_y)

    if not is_diamond(x, y, cx, cy, radius_x, radius_y):
        return False

    inner_radius_x = radius_x - thickness
    inner_radius_y = radius_y - thickness
    if inner_radius_x < 0 or inner_radius_y < 0:
        return True

    return not is_diamond(x, y, cx, cy, inner_radius_x, inner_radius_y)


def is_polygon(x, y, vertices):
    normalized_vertices = _validate_vertices('vertices', vertices, minimum_points=3)

    previous_x, previous_y = normalized_vertices[-1]
    inside = False

    for current_x, current_y in normalized_vertices:
        if _point_on_segment(x, y, previous_x, previous_y, current_x, current_y):
            return True

        crosses_scanline = (current_y > y) != (previous_y > y)
        if crosses_scanline:
            intersection_x = current_x + (y - current_y) * (previous_x - current_x) / (previous_y - current_y)
            if x < intersection_x:
                inside = not inside

        previous_x, previous_y = current_x, current_y

    return inside


def is_polygon_outline(x, y, vertices, thickness=1):
    normalized_vertices = _validate_vertices('vertices', vertices, minimum_points=3)
    return is_polyline(x, y, normalized_vertices, thickness=thickness, closed=True)