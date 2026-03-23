"""Public facade for procedural pixel-art export and 2D geometry helpers."""

import os
import sys

from pixel_engine import core as _core
from pixel_engine import export as _export
from pixel_engine import geometry as _geometry


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(PROJECT_ROOT, 'images')

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


is_rect = _geometry.is_rect
is_rect_outline = _geometry.is_rect_outline
is_line = _geometry.is_line
is_polyline = _geometry.is_polyline
is_circle = _geometry.is_circle
is_circle_outline = _geometry.is_circle_outline
is_ellipse = _geometry.is_ellipse
is_ellipse_outline = _geometry.is_ellipse_outline
is_diamond = _geometry.is_diamond
is_diamond_outline = _geometry.is_diamond_outline
is_polygon = _geometry.is_polygon
is_polygon_outline = _geometry.is_polygon_outline

__all__ = [
    'PROJECT_ROOT',
    'IMAGES_DIR',
    'is_rect',
    'is_rect_outline',
    'is_line',
    'is_polyline',
    'is_circle',
    'is_circle_outline',
    'is_ellipse',
    'is_ellipse_outline',
    'is_diamond',
    'is_diamond_outline',
    'is_polygon',
    'is_polygon_outline',
    'save_as_png',
    'save_as_png_from_pixels',
]


def _print_build_complete():
    print('Progress: [####################] 100% - Done!          ')


def _log(message, progress):
    if progress:
        print(message)


def _format_project_relative_path(path):
    try:
        return os.path.relpath(path, PROJECT_ROOT).replace('\\', '/')
    except ValueError:
        return path.replace('\\', '/')


def _build_named_pixels(name, width, height, fill_func, label, progress=True):
    _core.validate_export_inputs(width, height, fill_func)
    _log(f'[Pixel Factory] {label}: {name} ({width}x{height})', progress)
    pixels = _core.build_pixel_map(width, height, fill_func, progress=progress)
    if progress:
        _print_build_complete()
    return pixels


def _resolve_output_path(name, extension, output_dir=None):
    return _core.resolve_output_path(name, extension, IMAGES_DIR, output_dir=output_dir)


def save_as_png_from_pixels(name, W, H, pixels, palette=None, scale=8, output_dir=None, background=None, progress=True):
    """Writes a PNG file from a pre-built pixel map."""
    _core.validate_positive_dimension('W', W)
    _core.validate_positive_dimension('H', H)
    _core.validate_positive_dimension('scale', scale)

    image = _export.build_image(W, H, pixels, palette=palette, background=background)
    if scale != 1:
        image = _export.upscale_image(image, scale)

    path = _resolve_output_path(name, 'png', output_dir=output_dir)
    _export.write_png(path, image)
    _log(f'[Pixel Factory] Saved to: {_format_project_relative_path(path)}', progress)
    return path


def save_as_png(name, W, H, fill_func, palette=None, scale=8, output_dir=None, background=None, progress=True):
    """Builds pixels with fill_func(x, y, W, H) and writes a PNG file."""
    _core.validate_positive_dimension('scale', scale)
    pixels = _build_named_pixels(name, W, H, fill_func, label='Building', progress=progress)
    return save_as_png_from_pixels(
        name,
        W,
        H,
        pixels,
        palette=palette,
        scale=scale,
        output_dir=output_dir,
        background=background,
        progress=progress,
    )