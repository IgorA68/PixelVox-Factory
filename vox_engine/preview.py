import os
from dataclasses import dataclass

from palette_utils import build_palette


@dataclass(frozen=True)
class PreviewConfig:
    project_root: str
    models_dir: str
    views: tuple
    modes: tuple
    background: tuple
    panel_gap: int
    max_width: int
    max_height: int
    tile_width_scale: int
    tile_height_scale: int
    elevation_scale: int


def validate_preview_mode(mode, config):
    if mode not in config.modes:
        raise ValueError(f'preview mode must be one of {config.modes}, got {mode!r}')


def resolve_preview_output_name(name, mode):
    suffix = f'-{mode}'
    if name.endswith(suffix):
        return name
    return f'{name}{suffix}'


def build_palette_lookup(palette):
    return {
        index: tuple(color)
        for index, color in enumerate(build_palette(palette))
    }


def project_voxels(view, width, depth, height, voxels):
    if view == 'top':
        panel_width, panel_height = width, depth

        def to_pixel(voxel):
            return voxel.x, depth - 1 - voxel.y

        def visibility_key(voxel):
            return voxel.z
    elif view == 'front':
        panel_width, panel_height = width, height

        def to_pixel(voxel):
            return voxel.x, height - 1 - voxel.z

        def visibility_key(voxel):
            return voxel.y
    elif view == 'side':
        panel_width, panel_height = depth, height

        def to_pixel(voxel):
            return voxel.y, height - 1 - voxel.z

        def visibility_key(voxel):
            return voxel.x
    else:
        raise ValueError(f'Unsupported preview view: {view!r}')

    visible_voxels = {}
    for voxel in voxels:
        pixel = to_pixel(voxel)
        current = visible_voxels.get(pixel)
        voxel_key = visibility_key(voxel)
        if current is None or voxel_key >= current[0]:
            visible_voxels[pixel] = (voxel_key, voxel.c)

    return panel_width, panel_height, visible_voxels


def _require_image_module():
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError('PNG previews require Pillow. Install dependencies from requirements.txt.') from exc

    return Image


def _require_image_draw_module():
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise RuntimeError('PNG previews require Pillow. Install dependencies from requirements.txt.') from exc

    return Image, ImageDraw


def build_preview_panels(voxels, width, depth, height, palette, scale, config):
    image_module = _require_image_module()
    resampling_namespace = getattr(image_module, 'Resampling', image_module)
    palette_lookup = build_palette_lookup(palette)
    panels = []

    for view in config.views:
        panel_width, panel_height, visible_voxels = project_voxels(view, width, depth, height, voxels)
        panel = image_module.new('RGBA', (panel_width, panel_height), config.background)
        pixels = panel.load()

        for (pixel_x, pixel_y), (_, color_index) in visible_voxels.items():
            pixels[pixel_x, pixel_y] = palette_lookup[color_index]

        panels.append(panel.resize(
            (panel_width * scale, panel_height * scale),
            resample=resampling_namespace.NEAREST,
        ))

    return panels


def build_preview_panel(view, voxels, width, depth, height, palette, scale, config):
    image_module = _require_image_module()
    resampling_namespace = getattr(image_module, 'Resampling', image_module)
    palette_lookup = build_palette_lookup(palette)
    panel_width, panel_height, visible_voxels = project_voxels(view, width, depth, height, voxels)
    panel = image_module.new('RGBA', (panel_width, panel_height), config.background)
    pixels = panel.load()

    for (pixel_x, pixel_y), (_, color_index) in visible_voxels.items():
        pixels[pixel_x, pixel_y] = palette_lookup[color_index]

    return panel.resize(
        (panel_width * scale, panel_height * scale),
        resample=resampling_namespace.NEAREST,
    )


def get_preview_dimensions(width, depth, height, scale, mode, config):
    validate_preview_mode(mode, config)

    if mode == 'top':
        return width * scale, depth * scale

    if mode == 'orthographic':
        panel_widths = (width * scale, width * scale, depth * scale)
        panel_heights = (depth * scale, height * scale, height * scale)
        total_width = sum(panel_widths) + config.panel_gap * (len(panel_widths) - 1)
        total_height = max(panel_heights)
        return total_width, total_height

    if mode == 'isometric':
        scaled_tile_width = max(2, config.tile_width_scale * scale)
        scaled_tile_height = max(1, config.tile_height_scale * scale)
        scaled_elevation = max(1, config.elevation_scale * scale)
        canvas_width = (width + depth) * scaled_tile_width // 2 + scaled_tile_width * 2
        canvas_height = (width + depth) * scaled_tile_height // 2 + height * scaled_elevation + scaled_tile_height * 3
        return canvas_width, canvas_height

    orthographic_width, orthographic_height = get_preview_dimensions(width, depth, height, scale, mode='orthographic', config=config)
    isometric_width, isometric_height = get_preview_dimensions(width, depth, height, scale, mode='isometric', config=config)
    return max(orthographic_width, isometric_width), orthographic_height + config.panel_gap + isometric_height


def resolve_preview_scale(width, depth, height, requested_scale, mode, config):
    for candidate_scale in range(requested_scale, 0, -1):
        preview_width, preview_height = get_preview_dimensions(width, depth, height, candidate_scale, mode, config)
        if preview_width <= config.max_width and preview_height <= config.max_height:
            return candidate_scale

    return 1


def shade_color(color, factor):
    red, green, blue, alpha = color
    return (
        max(0, min(255, int(red * factor))),
        max(0, min(255, int(green * factor))),
        max(0, min(255, int(blue * factor))),
        alpha,
    )


def build_isometric_preview(voxels, width, depth, height, palette, scale, config):
    image_module, image_draw_module = _require_image_draw_module()

    palette_lookup = build_palette_lookup(palette)
    scaled_tile_width = max(2, config.tile_width_scale * scale)
    scaled_tile_height = max(1, config.tile_height_scale * scale)
    scaled_elevation = max(1, config.elevation_scale * scale)
    base_x = depth * scaled_tile_width // 2 + scaled_tile_width
    base_y = height * scaled_elevation + scaled_tile_height
    canvas_width = (width + depth) * scaled_tile_width // 2 + scaled_tile_width * 2
    canvas_height = (width + depth) * scaled_tile_height // 2 + height * scaled_elevation + scaled_tile_height * 3

    image = image_module.new('RGBA', (canvas_width, canvas_height), config.background)
    draw = image_draw_module.Draw(image)

    for voxel in sorted(voxels, key=lambda item: (item.x + item.y, item.z, item.x)):
        color = palette_lookup[voxel.c]
        top_color = color
        left_color = shade_color(color, 0.82)
        right_color = shade_color(color, 0.64)

        center_x = base_x + (voxel.x - voxel.y) * scaled_tile_width // 2
        center_y = base_y + (voxel.x + voxel.y) * scaled_tile_height // 2 - voxel.z * scaled_elevation
        half_width = scaled_tile_width // 2
        half_height = scaled_tile_height // 2

        top = [
            (center_x, center_y - half_height),
            (center_x + half_width, center_y),
            (center_x, center_y + half_height),
            (center_x - half_width, center_y),
        ]
        left = [
            (center_x - half_width, center_y),
            (center_x, center_y + half_height),
            (center_x, center_y + half_height + scaled_elevation),
            (center_x - half_width, center_y + scaled_elevation),
        ]
        right = [
            (center_x + half_width, center_y),
            (center_x, center_y + half_height),
            (center_x, center_y + half_height + scaled_elevation),
            (center_x + half_width, center_y + scaled_elevation),
        ]

        draw.polygon(left, fill=left_color)
        draw.polygon(right, fill=right_color)
        draw.polygon(top, fill=top_color)

    return image


def build_preview_image(voxels, width, depth, height, palette, scale, mode, config):
    validate_preview_mode(mode, config)
    image_module = _require_image_module()

    if mode == 'orthographic':
        panels = build_preview_panels(voxels, width, depth, height, palette, scale, config)
        total_width = sum(panel.width for panel in panels) + config.panel_gap * (len(panels) - 1)
        total_height = max(panel.height for panel in panels)
        preview = image_module.new('RGBA', (total_width, total_height), config.background)
        x_offset = 0
        for panel in panels:
            preview.paste(panel, (x_offset, 0))
            x_offset += panel.width + config.panel_gap
        return preview

    if mode == 'top':
        return build_preview_panel('top', voxels, width, depth, height, palette, scale, config)

    if mode == 'isometric':
        return build_isometric_preview(voxels, width, depth, height, palette, scale, config)

    orthographic = build_preview_image(voxels, width, depth, height, palette, scale, mode='orthographic', config=config)
    isometric = build_preview_image(voxels, width, depth, height, palette, scale, mode='isometric', config=config)
    combined = image_module.new(
        'RGBA',
        (max(orthographic.width, isometric.width), orthographic.height + config.panel_gap + isometric.height),
        config.background,
    )
    combined.paste(orthographic, ((combined.width - orthographic.width) // 2, 0))
    combined.paste(isometric, ((combined.width - isometric.width) // 2, orthographic.height + config.panel_gap))
    return combined


def format_preview_output_path(path, project_root, preview_name):
    try:
        relative_dir = os.path.relpath(os.path.dirname(path), project_root).replace('\\', '/')
    except ValueError:
        relative_dir = os.path.dirname(path).replace('\\', '/')
    return f'{relative_dir}/{preview_name}.png'