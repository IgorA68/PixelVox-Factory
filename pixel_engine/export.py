import os

from palette_utils import build_palette


def _require_image_module():
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError('PNG export requires Pillow. Install dependencies from requirements.txt.') from exc

    return Image


def _normalize_rgba_color(name, color):
    if color is None:
        return (0, 0, 0, 0)

    if not isinstance(color, (tuple, list)):
        raise TypeError(f'{name} must be an RGB or RGBA tuple, got {color!r}')

    rgba = tuple(color)
    if len(rgba) == 3:
        rgba = (*rgba, 255)
    elif len(rgba) != 4:
        raise ValueError(f'{name} must have 3 or 4 channels, got {rgba!r}')

    normalized_channels = []
    for channel in rgba:
        if isinstance(channel, bool) or not isinstance(channel, int):
            raise TypeError(f'{name} channel must be an integer, got {channel!r}')
        if not 0 <= channel <= 255:
            raise ValueError(f'{name} channel must be between 0 and 255, got {channel!r}')
        normalized_channels.append(channel)

    return tuple(normalized_channels)


def build_palette_lookup(palette):
    return {
        index: tuple(color)
        for index, color in enumerate(build_palette(palette))
    }


def build_image(width, height, pixels, palette=None, background=None):
    image_module = _require_image_module()
    palette_lookup = build_palette_lookup(palette)
    background_color = _normalize_rgba_color('background', background)
    image = image_module.new('RGBA', (width, height), background_color)
    image_pixels = image.load()

    for (x, y), color_index in pixels.items():
        image_pixels[x, y] = palette_lookup[color_index]

    return image


def upscale_image(image, scale):
    image_module = _require_image_module()
    resampling_namespace = getattr(image_module, 'Resampling', image_module)
    return image.resize((image.width * scale, image.height * scale), resample=resampling_namespace.NEAREST)


def write_png(path, image):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    image.save(path)