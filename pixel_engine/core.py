import os


def validate_positive_dimension(name, value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f'{name} must be a positive integer, got {value!r}')

    if value <= 0:
        raise ValueError(f'{name} must be a positive integer, got {value!r}')


def validate_export_inputs(width, height, fill_func):
    for dimension_name, dimension_value in [('W', width), ('H', height)]:
        validate_positive_dimension(dimension_name, dimension_value)

    if not callable(fill_func):
        raise TypeError('fill_func must be callable')


def normalize_color_value(color):
    if isinstance(color, bool):
        return 1 if color else None

    if isinstance(color, int):
        if color < 0:
            raise ValueError(f'fill_func returned a negative palette index: {color}')
        return color or None

    if not color:
        return None

    return 1


def print_progress(y, height, enabled=True):
    if not enabled:
        return

    if y % max(1, height // 20) != 0:
        return

    progress_percent = int((y / height) * 100)
    progress_bar = f"{'#' * (progress_percent // 5)}{'.' * (20 - progress_percent // 5)}"
    print(f'Progress: [{progress_bar}] {progress_percent}%', end='\r')


def build_pixel_map(width, height, fill_func, progress=True):
    pixels = {}

    for y in range(height):
        print_progress(y, height, enabled=progress)

        for x in range(width):
            color = normalize_color_value(fill_func(x, y, width, height))
            if color is not None:
                pixels[(x, y)] = color

    return pixels


def resolve_output_path(name, extension, images_dir, output_dir=None):
    target_dir = output_dir or images_dir
    os.makedirs(target_dir, exist_ok=True)
    return os.path.join(target_dir, f'{name}.{extension}')