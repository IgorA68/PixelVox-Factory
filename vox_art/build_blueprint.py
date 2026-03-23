import argparse
import os

from vox_art import engine
from vox_art.blueprint_utils import build_fill_func
from vox_art.blueprint_utils import get_blueprint_dimensions
from vox_art.blueprint_utils import get_blueprint_palette_overrides
from vox_art.blueprint_utils import load_blueprint_module
from vox_art.blueprint_utils import resolve_blueprint_path
from vox_art.blueprint_utils import validate_blueprint_module


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW_ASSETS_DIR = os.path.join(PROJECT_ROOT, 'vox_preview_assets')
engine_vox = engine
SHOWCASE_PREVIEW_MODELS = [
    {'blueprint': 'house', 'output_name': 'house'},
    {'blueprint': 'hills', 'output_name': 'hills'},
    {'blueprint': 'realistic_tree_vox', 'output_name': 'realistic_tree_vox', 'seed': 7},
    {'blueprint': 'rocket', 'output_name': 'rocket'},
    {'blueprint': 'tower', 'output_name': 'tower'},
    {'blueprint': 'vehicle', 'output_name': 'vehicle'},
    {'blueprint': 'negative_space_arch', 'output_name': 'cave'},
]


def _validate_dimensions(width, depth, height):
    for name, value in [('width', width), ('depth', depth), ('height', height)]:
        if value <= 0:
            raise ValueError(f'{name} must be a positive integer, got {value}')


def _resolve_blueprint_build_context(blueprint_arg, width=None, depth=None, height=None, seed=None, output_name=None):
    blueprint_path = resolve_blueprint_path(blueprint_arg)
    if not os.path.exists(blueprint_path):
        raise FileNotFoundError(f'Blueprint not found: {blueprint_path}')

    module = load_blueprint_module(blueprint_path)
    validate_blueprint_module(module)

    default_width, default_depth, default_height = get_blueprint_dimensions(module)
    width = width if width is not None else default_width
    depth = depth if depth is not None else default_depth
    height = height if height is not None else default_height
    _validate_dimensions(width, depth, height)

    base_output_name = os.path.splitext(os.path.basename(blueprint_path))[0]
    if output_name:
        resolved_output_name = output_name
    elif seed is not None:
        resolved_output_name = f'{base_output_name}_seed_{seed}'
    else:
        resolved_output_name = base_output_name

    fill_func = build_fill_func(module, seed=seed)
    palette_overrides = get_blueprint_palette_overrides(module)
    return resolved_output_name, width, depth, height, fill_func, palette_overrides


def build_blueprint_outputs(blueprint_arg, width=None, depth=None, height=None, seed=None, output_name=None,
                            preview_png=False, preview_scale=8, preview_mode='orthographic', preview_output_dir=None,
                            export_vox=True, output_dir=None, quiet=False):
    resolved_output_name, width, depth, height, fill_func, palette_overrides = _resolve_blueprint_build_context(
        blueprint_arg,
        width=width,
        depth=depth,
        height=height,
        seed=seed,
        output_name=output_name,
    )
    engine.save_outputs(
        resolved_output_name,
        width,
        depth,
        height,
        fill_func,
        palette=palette_overrides,
        preview_png=preview_png,
        preview_scale=preview_scale,
        preview_mode=preview_mode,
        preview_output_dir=preview_output_dir,
        export_vox=export_vox,
        output_dir=output_dir,
        progress=not quiet,
    )


def build_showcase_previews(preview_scale=8, preview_mode='isometric', preview_output_dir=PREVIEW_ASSETS_DIR,
                            quiet=False):
    for entry in SHOWCASE_PREVIEW_MODELS:
        build_blueprint_outputs(
            entry['blueprint'],
            seed=entry.get('seed'),
            output_name=entry['output_name'],
            preview_png=True,
            preview_scale=preview_scale,
            preview_mode=preview_mode,
            preview_output_dir=preview_output_dir,
            export_vox=False,
            quiet=quiet,
        )


def main():
    parser = argparse.ArgumentParser(description='Build a .vox model from a blueprint.')
    parser.add_argument('blueprint', nargs='?', help='Blueprint name from vox_blueprints/ or a direct .py path.')
    parser.add_argument('--width', type=int, help='Override blueprint width.')
    parser.add_argument('--depth', type=int, help='Override blueprint depth.')
    parser.add_argument('--height', type=int, help='Override blueprint height.')
    parser.add_argument('--seed', type=int, help='Optional deterministic seed for blueprints that support seeded variants.')
    parser.add_argument('--output-name', help='Override output model name.')
    parser.add_argument('--output-dir', help='Override the output directory used for generated .vox files.')
    parser.add_argument('--preview-png', action='store_true', help='Also save a PNG preview sheet with top, front, and side projections.')
    parser.add_argument('--preview-only', action='store_true', help='Generate only the PNG preview output and skip writing a .vox file.')
    parser.add_argument('--preview-scale', type=int, default=8, help='Pixel scale for PNG previews when --preview-png is enabled.')
    parser.add_argument('--preview-mode', choices=engine.PREVIEW_MODES, default='orthographic', help='Preview rendering mode for PNG output.')
    parser.add_argument('--quiet', action='store_true', help='Suppress build progress and status output.')
    parser.add_argument('--batch-preview-demo-set', action='store_true', help='Generate PNG previews for the curated showcase set into vox_preview_assets/.')
    parser.add_argument('--batch-output-dir', help='Override the output directory used by --batch-preview-demo-set.')
    args = parser.parse_args()

    if args.batch_preview_demo_set:
        build_showcase_previews(
            preview_scale=args.preview_scale,
            preview_mode=args.preview_mode,
            preview_output_dir=args.batch_output_dir or PREVIEW_ASSETS_DIR,
            quiet=args.quiet,
        )
        return

    if not args.blueprint:
        parser.error('blueprint is required unless --batch-preview-demo-set is used')

    build_blueprint_outputs(
        args.blueprint,
        width=args.width,
        depth=args.depth,
        height=args.height,
        seed=args.seed,
        output_name=args.output_name,
        preview_png=args.preview_png or args.preview_only,
        preview_scale=args.preview_scale,
        preview_mode=args.preview_mode,
        export_vox=not args.preview_only,
        output_dir=args.output_dir,
        quiet=args.quiet,
    )


if __name__ == '__main__':
    main()
