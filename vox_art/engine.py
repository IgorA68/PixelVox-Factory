"""Public facade for voxel export, preview rendering, and geometry helpers."""

import os
import sys

from pyvox.models import Model, Size, Vox, Voxel
from pyvox.writer import VoxWriter

from vox_engine import core as _core
from vox_engine import export as _export
from vox_engine import geometry as _geometry
from vox_engine import preview as _preview


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, 'vox_models')
PREVIEW_VIEWS = ('top', 'front', 'side')
PREVIEW_MODES = ('orthographic', 'isometric', 'both', 'top')
PREVIEW_BACKGROUND = (245, 242, 235, 255)
PREVIEW_PANEL_GAP = 2
MAX_PREVIEW_WIDTH = 1600
MAX_PREVIEW_HEIGHT = 1600
ISOMETRIC_TILE_WIDTH_SCALE = 2
ISOMETRIC_TILE_HEIGHT_SCALE = 1
ISOMETRIC_ELEVATION_SCALE = 1

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)


_validate_positive_dimension = _core.validate_positive_dimension
_validate_export_inputs = _core.validate_export_inputs
is_sphere = _geometry.is_sphere
is_cylinder = _geometry.is_cylinder
is_cone = _geometry.is_cone
is_capsule = _geometry.is_capsule
is_torus = _geometry.is_torus
is_box = _geometry.is_box

__all__ = [
    'PROJECT_ROOT',
    'MODELS_DIR',
    'PREVIEW_VIEWS',
    'PREVIEW_MODES',
    'PREVIEW_BACKGROUND',
    'PREVIEW_PANEL_GAP',
    'MAX_PREVIEW_WIDTH',
    'MAX_PREVIEW_HEIGHT',
    'ISOMETRIC_TILE_WIDTH_SCALE',
    'ISOMETRIC_TILE_HEIGHT_SCALE',
    'ISOMETRIC_ELEVATION_SCALE',
    'is_sphere',
    'is_cylinder',
    'is_cone',
    'is_capsule',
    'is_torus',
    'is_box',
    'save_as_vox',
    'save_preview_png',
    'save_outputs',
    'save_as_vox_from_voxels',
    'save_preview_png_from_voxels',
]


def _preview_config():
    return _preview.PreviewConfig(
        project_root=PROJECT_ROOT,
        models_dir=MODELS_DIR,
        views=PREVIEW_VIEWS,
        modes=PREVIEW_MODES,
        background=PREVIEW_BACKGROUND,
        panel_gap=PREVIEW_PANEL_GAP,
        max_width=MAX_PREVIEW_WIDTH,
        max_height=MAX_PREVIEW_HEIGHT,
        tile_width_scale=ISOMETRIC_TILE_WIDTH_SCALE,
        tile_height_scale=ISOMETRIC_TILE_HEIGHT_SCALE,
        elevation_scale=ISOMETRIC_ELEVATION_SCALE,
    )


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


def _build_named_voxels(name, width, depth, height, fill_func, label, progress=True):
    _validate_export_inputs(width, depth, height, fill_func)
    _log(f'[VOX Factory] {label}: {name} ({width}x{depth}x{height})', progress)
    voxels = _build_voxel_list(width, depth, height, fill_func, progress=progress)
    if progress:
        _print_build_complete()
    return voxels


def _build_voxel_list(width, depth, height, fill_func, progress=True):
    return _core.build_voxel_list(width, depth, height, fill_func, voxel_cls=Voxel, progress=progress)


def _resolve_output_path(name, extension, output_dir=None):
    return _core.resolve_output_path(name, extension, MODELS_DIR, output_dir=output_dir)


def _validate_preview_mode(mode):
    return _preview.validate_preview_mode(mode, _preview_config())


def _get_preview_dimensions(width, depth, height, scale, mode):
    return _preview.get_preview_dimensions(width, depth, height, scale, mode, _preview_config())


def _resolve_preview_scale(width, depth, height, requested_scale, mode):
    return _preview.resolve_preview_scale(width, depth, height, requested_scale, mode, _preview_config())


def _shade_color(color, factor):
    return _preview.shade_color(color, factor)


def _build_isometric_preview(voxels, width, depth, height, palette, scale):
    return _preview.build_isometric_preview(voxels, width, depth, height, palette, scale, _preview_config())


def _build_preview_image(voxels, width, depth, height, palette, scale, mode):
    return _preview.build_preview_image(voxels, width, depth, height, palette, scale, mode, _preview_config())


def save_as_vox_from_voxels(name, W, D, H, voxels, palette=None, output_dir=None, progress=True):
    path = _resolve_output_path(name, 'vox', output_dir=output_dir)
    vox_data = _export.build_vox_data(
        W,
        D,
        H,
        voxels,
        palette=palette,
        vox_cls=Vox,
        model_cls=Model,
        size_cls=Size,
    )
    _export.write_vox(path, vox_data, writer_cls=VoxWriter)
    _log(f'[VOX Factory] Saved to: {_format_project_relative_path(path)} (Voxels: {len(voxels)})', progress)
    return path


def save_preview_png_from_voxels(name, W, D, H, voxels, palette=None, scale=8, mode='orthographic', output_dir=None,
                                 progress=True):
    _validate_positive_dimension('scale', scale)
    _validate_preview_mode(mode)

    effective_scale = _resolve_preview_scale(W, D, H, scale, mode)
    if effective_scale != scale:
        preview_width, preview_height = _get_preview_dimensions(W, D, H, effective_scale, mode)
        _log(
            f'[VOX Factory] Preview scale adjusted from {scale} to {effective_scale} '
            f'to fit within {MAX_PREVIEW_WIDTH}x{MAX_PREVIEW_HEIGHT} ({preview_width}x{preview_height}).',
            progress,
        )

    preview = _build_preview_image(voxels, W, D, H, palette, effective_scale, mode)
    preview_name = _preview.resolve_preview_output_name(name, mode)
    path = _resolve_output_path(preview_name, 'png', output_dir=output_dir)
    preview.save(path)
    formatted_path = _preview.format_preview_output_path(path, PROJECT_ROOT, preview_name)
    _log(f'[VOX Factory] Saved preview to: {formatted_path}', progress)
    return path


def save_outputs(name, W, D, H, fill_func, palette=None, preview_png=False, preview_scale=8,
                 preview_mode='orthographic', preview_output_dir=None, export_vox=True, vox_output_dir=None,
                 output_dir=None, progress=True):
    if preview_png:
        _validate_positive_dimension('scale', preview_scale)
        _validate_preview_mode(preview_mode)

    vox_output_dir = output_dir if output_dir is not None else vox_output_dir
    voxels = _build_named_voxels(name, W, D, H, fill_func, label='Building', progress=progress)

    if export_vox:
        save_as_vox_from_voxels(name, W, D, H, voxels, palette=palette, output_dir=vox_output_dir, progress=progress)

    if preview_png:
        save_preview_png_from_voxels(
            name,
            W,
            D,
            H,
            voxels,
            palette=palette,
            scale=preview_scale,
            mode=preview_mode,
            output_dir=preview_output_dir,
            progress=progress,
        )


def save_preview_png(name, W, D, H, fill_func, palette=None, scale=8, mode='orthographic', output_dir=None,
                     progress=True):
    _validate_positive_dimension('scale', scale)
    _validate_preview_mode(mode)
    voxels = _build_named_voxels(name, W, D, H, fill_func, label='Building preview', progress=progress)
    return save_preview_png_from_voxels(
        name,
        W,
        D,
        H,
        voxels,
        palette=palette,
        scale=scale,
        mode=mode,
        output_dir=output_dir,
        progress=progress,
    )


def save_as_vox(name, W, D, H, fill_func, palette=None, output_dir=None, progress=True):
    voxels = _build_named_voxels(name, W, D, H, fill_func, label='Building', progress=progress)
    return save_as_vox_from_voxels(name, W, D, H, voxels, palette=palette, output_dir=output_dir, progress=progress)
