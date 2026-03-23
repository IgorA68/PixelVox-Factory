import argparse
import os

from pixel_art import engine
from pixel_art.blueprint_utils import build_fill_func
from pixel_art.blueprint_utils import get_blueprint_dimensions
from pixel_art.blueprint_utils import get_blueprint_palette_overrides
from pixel_art.blueprint_utils import load_blueprint_module
from pixel_art.blueprint_utils import resolve_blueprint_path
from pixel_art.blueprint_utils import validate_blueprint_module


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIXEL_PREVIEW_ASSETS_DIR = os.path.join(PROJECT_ROOT, 'images')
SHOWCASE_PIXEL_BLUEPRINTS = [
    {'blueprint': 'gem_icon', 'seed': 7, 'scale': 8, 'output_name': 'gem_icon'},
    {'blueprint': 'potion_icon', 'seed': 7, 'scale': 8, 'output_name': 'potion_icon'},
    {'blueprint': 'grass_tile', 'seed': 7, 'scale': 8, 'output_name': 'grass_tile'},
    {'blueprint': 'crate_prop', 'scale': 8, 'output_name': 'crate_prop'},
    {'blueprint': 'bush_prop', 'seed': 7, 'scale': 8, 'output_name': 'bush_prop'},
    {'blueprint': 'stone_floor_tile', 'seed': 7, 'scale': 8, 'output_name': 'stone_floor_tile'},
    {'blueprint': 'tiny_face_avatar', 'seed': 7, 'scale': 6, 'output_name': 'tiny_face_avatar'},
]


def _validate_dimensions(width, height):
    for name, value in [('width', width), ('height', height)]:
        if value <= 0:
            raise ValueError(f'{name} must be a positive integer, got {value}')


def _resolve_blueprint_build_context(blueprint_arg, width=None, height=None, seed=None, output_name=None):
    blueprint_path = resolve_blueprint_path(blueprint_arg)
    if not os.path.exists(blueprint_path):
        raise FileNotFoundError(f'Blueprint not found: {blueprint_path}')

    module = load_blueprint_module(blueprint_path)
    validate_blueprint_module(module)

    default_width, default_height = get_blueprint_dimensions(module)
    width = width if width is not None else default_width
    height = height if height is not None else default_height
    _validate_dimensions(width, height)

    base_output_name = os.path.splitext(os.path.basename(blueprint_path))[0]
    if output_name:
        resolved_output_name = output_name
    elif seed is not None:
        resolved_output_name = f'{base_output_name}_seed_{seed}'
    else:
        resolved_output_name = base_output_name

    fill_func = build_fill_func(module, seed=seed)
    palette_overrides = get_blueprint_palette_overrides(module)
    return resolved_output_name, width, height, fill_func, palette_overrides


def build_blueprint_output(blueprint_arg, width=None, height=None, seed=None, output_name=None, output_dir=None,
                           scale=8, quiet=False, background=None):
    resolved_output_name, width, height, fill_func, palette_overrides = _resolve_blueprint_build_context(
        blueprint_arg,
        width=width,
        height=height,
        seed=seed,
        output_name=output_name,
    )
    return engine.save_as_png(
        resolved_output_name,
        width,
        height,
        fill_func,
        palette=palette_overrides,
        scale=scale,
        output_dir=output_dir,
        background=background,
        progress=not quiet,
    )


def build_showcase_pixel_outputs(output_dir=PIXEL_PREVIEW_ASSETS_DIR, quiet=False):
    for entry in SHOWCASE_PIXEL_BLUEPRINTS:
        build_blueprint_output(
            entry['blueprint'],
            seed=entry.get('seed'),
            output_name=entry['output_name'],
            output_dir=output_dir,
            scale=entry.get('scale', 8),
            quiet=quiet,
        )


def main():
    parser = argparse.ArgumentParser(description='Build a PNG image from a pixel blueprint.')
    parser.add_argument('blueprint', help='Blueprint name from pixel_blueprints/ or a direct .py path.')
    parser.add_argument('--width', type=int, help='Override blueprint width.')
    parser.add_argument('--height', type=int, help='Override blueprint height.')
    parser.add_argument('--seed', type=int, help='Optional deterministic seed for blueprints that support seeded variants.')
    parser.add_argument('--output-name', help='Override output image name.')
    parser.add_argument('--output-dir', help='Override the output directory used for generated PNG files.')
    parser.add_argument('--scale', type=int, default=8, help='Nearest-neighbor upscale factor for the generated PNG.')
    parser.add_argument('--quiet', action='store_true', help='Suppress build progress and status output.')
    args = parser.parse_args()

    build_blueprint_output(
        args.blueprint,
        width=args.width,
        height=args.height,
        seed=args.seed,
        output_name=args.output_name,
        output_dir=args.output_dir,
        scale=args.scale,
        quiet=args.quiet,
    )


if __name__ == '__main__':
    main()