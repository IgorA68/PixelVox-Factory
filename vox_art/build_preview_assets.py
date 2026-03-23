import argparse

from vox_art.build_blueprint import PREVIEW_ASSETS_DIR
from vox_art.build_blueprint import build_showcase_previews


def main():
    parser = argparse.ArgumentParser(description='Generate PNG previews for the curated showcase set.')
    parser.add_argument('--preview-scale', type=int, default=8, help='Pixel scale used for generated showcase previews.')
    parser.add_argument('--preview-mode', choices=('orthographic', 'isometric', 'both', 'top'), default='isometric', help='Preview rendering mode for showcase assets.')
    parser.add_argument('--output-dir', default=PREVIEW_ASSETS_DIR, help='Directory for generated showcase PNG files.')
    parser.add_argument('--quiet', action='store_true', help='Suppress build progress and status output during batch generation.')
    args = parser.parse_args()

    build_showcase_previews(
        preview_scale=args.preview_scale,
        preview_mode=args.preview_mode,
        preview_output_dir=args.output_dir,
        quiet=args.quiet,
    )


if __name__ == '__main__':
    main()
