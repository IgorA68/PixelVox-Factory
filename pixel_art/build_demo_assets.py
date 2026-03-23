import argparse

from pixel_art.build_blueprint import PIXEL_PREVIEW_ASSETS_DIR
from pixel_art.build_blueprint import build_showcase_pixel_outputs


def main():
    parser = argparse.ArgumentParser(description='Generate PNG files for the curated pixel-art showcase set.')
    parser.add_argument('--output-dir', default=PIXEL_PREVIEW_ASSETS_DIR, help='Directory for generated showcase PNG files.')
    parser.add_argument('--quiet', action='store_true', help='Suppress build progress and status output during batch generation.')
    args = parser.parse_args()

    build_showcase_pixel_outputs(output_dir=args.output_dir, quiet=args.quiet)


if __name__ == '__main__':
    main()