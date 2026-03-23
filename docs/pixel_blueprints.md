# Pixel Blueprint Guide

This guide explains the 2D procedural blueprint path used for pixel-art output in this repository.

The core workflow matches the voxel side of the project:

1. describe an asset in plain language;
2. ask an AI coding agent to turn that request into a blueprint;
3. build the result through the pixel-art CLI;
4. inspect the PNG output;
5. refine the blueprint, palette, or seed and build again.

The important difference is that the final artifact is a palette-based PNG instead of a `.vox` model.

## What A Pixel Blueprint Is

A pixel blueprint is a Python module that decides which palette index belongs at each `(x, y)` coordinate in an output image.

The 2D runtime calls the blueprint once per pixel candidate and writes the result into a PNG.

Like the voxel side of the repository, this keeps the result:

- deterministic;
- inspectable as code;
- versionable in Git;
- easy to vary through dimensions, palette overrides, and optional seed values.

## Contract

Each pixel blueprint must define a function with this shape:

```python
def make_image(x, y, W, H):
    ...
    return color_index_or_zero
```

Seed-aware blueprints may optionally accept a fifth argument:

```python
def make_image(x, y, W, H, seed=None):
    ...
    return color_index_or_zero
```

The runtime treats return values as follows:

- `0`, `None`, and `False` mean transparent pixel;
- positive integers mean palette indices;
- other truthy non-integer values normalize to palette index `1` for compatibility;
- negative integers are rejected.

## Optional Module Metadata

Pixel blueprints follow the same general metadata style as voxel blueprints.

Supported optional constants:

```python
DEFAULT_W = 16
DEFAULT_H = 16

BLUEPRINT_DISPLAY_NAME = 'Potion Icon'
BLUEPRINT_DESCRIPTION = 'A tiny inventory icon with a readable silhouette.'

RECOMMENDED_W = 16
RECOMMENDED_H = 16

BLUEPRINT_PALETTE_OVERRIDES = {
    130: (204, 236, 255),
    131: (88, 160, 214),
}
```

If recommended dimensions are omitted, tooling falls back to `DEFAULT_W` and `DEFAULT_H`.

Palette overrides are optional and only replace the specified slots in the baseline project palette.

## Runtime API

Pixel blueprints should import the public 2D facade directly:

```python
from pixel_art import engine as ep
```

Current helper surface:

- `ep.is_rect(...)`
- `ep.is_rect_outline(...)`
- `ep.is_line(...)`
- `ep.is_polyline(...)`
- `ep.is_circle(...)`
- `ep.is_circle_outline(...)`
- `ep.is_ellipse(...)`
- `ep.is_ellipse_outline(...)`
- `ep.is_diamond(...)`
- `ep.is_diamond_outline(...)`
- `ep.is_polygon(...)`
- `ep.is_polygon_outline(...)`
- `ep.save_as_png(...)`

The main build path used by CLI and tests is still contract-first: define `make_image(...)`, then let the runtime evaluate it.

The practical rule of thumb is:

- use `ep.is_line(...)` for one-off strokes, stems, seams, and simple contour accents;
- use `ep.is_rect_outline(...)` for frames, boxes, windows, panel borders, and UI-like tiles;
- use `ep.is_polyline(...)` for open or closed multi-segment outlines;
- use `ep.is_circle_outline(...)`, `ep.is_ellipse_outline(...)`, and `ep.is_diamond_outline(...)` for eyes, bottles, shields, gems, halos, and ring-like silhouettes;
- use `ep.is_polygon(...)` for filled irregular silhouettes that would be awkward to express as rectangles, ellipses, or diamonds.
- use `ep.is_polygon_outline(...)` when you need the contour of an irregular closed shape without filling its interior.

For example, a framed panel can now be written directly instead of subtracting one rectangle from another by hand:

```python
if ep.is_rect_outline(x, y, 2, 2, W - 3, H - 3, thickness=1):
    return 122
```

## Minimal Example

This example shows the smallest useful pattern: transparent background plus one readable silhouette.

```python
DEFAULT_W = 16
DEFAULT_H = 16
BLUEPRINT_DISPLAY_NAME = 'Simple Gem'
BLUEPRINT_DESCRIPTION = 'A tiny gem icon.'

from pixel_art import engine as ep


def make_image(x, y, W, H):
    cx = W // 2
    cy = H // 2

    if ep.is_diamond(x, y, cx, cy, 3, 5):
        return 120

    return 0
```

This is enough to prove the contract, but it does not yet explain outline, highlight, or material separation.

## Layered Example

This example shows the more useful repository style: silhouette, outline, fill, and highlight separation.

```python
DEFAULT_W = 16
DEFAULT_H = 16
BLUEPRINT_DISPLAY_NAME = 'Layered Gem'
BLUEPRINT_DESCRIPTION = 'A gem icon with outline, fill, and highlight.'
BLUEPRINT_PALETTE_OVERRIDES = {
    120: (93, 174, 255),
    121: (210, 244, 255),
    122: (34, 92, 188),
    123: (34, 58, 120),
}

from pixel_art import engine as ep


def make_image(x, y, W, H):
    cx = W // 2
    cy = H // 2

    if not ep.is_diamond(x, y, cx, cy, 3, 5):
        return 0

    if not ep.is_diamond(x, y, cx, cy, 2, 4):
        return 123

    if x <= cx and y <= cy:
        return 121

    if x >= cx + 2 or y >= cy + 2:
        return 122

    return 120
```

This is the preferred direction for most game-facing assets in this repository: simple layered readability instead of noisy detail.

## CLI And GUI Workflow

Build a pixel blueprint with its default size:

```bash
python -m pixel_art.build_blueprint gem_icon
```

Override dimensions and scale:

```bash
python -m pixel_art.build_blueprint potion_icon --width 16 --height 16 --scale 8
```

Build a deterministic seeded variant:

```bash
python -m pixel_art.build_blueprint tiny_face_avatar --seed 7 --scale 6
```

Write output to a custom directory:

```bash
python -m pixel_art.build_blueprint grass_tile --output-dir exports
```

Generated PNG files go to `images/` by default unless `--output-dir` is provided.

To regenerate the current curated pixel-art showcase set in one pass, run:

```bash
python -m pixel_art.build_demo_assets
```

This is useful for quick review passes, release prep, or checking how the current demo set reads together after blueprint changes.

If you prefer the interactive route, launch the separate pixel-art GUI:

```bash
python -m pixel_art.gui_launcher
```

The GUI is intentionally separate from the voxel launcher so both workflows can stay simple and mode-specific.

## How This Relates To The Voxel Path

The voxel and pixel-art systems now share the same high-level philosophy:

- both are procedural blueprints;
- both are intended to be authored or assisted by AI through readable code;
- both use optional metadata and seed support;
- both prefer stable public facades over direct internal imports.

They intentionally diverge at the runtime level:

- voxel output uses `make_model(x, y, z, W, D, H)` and `.vox` export;
- pixel-art output uses `make_image(x, y, W, H)` and PNG export.

That separation keeps the 2D path simple and avoids turning the voxel engine into a multi-mode special case.

## Suggested First Asset Types

The most useful early blueprint categories are:

- inventory icons;
- terrain tiles;
- props and decor;
- simple NPC or avatar placeholders.

These map well onto prototype-heavy game workflows and are usually more valuable than trying to jump directly into complex illustration.

## Contributor Notes

- Prefer transparent backgrounds unless the asset category clearly needs a solid tile.
- Prefer readable silhouettes over fine-grain noise.
- Use palette indices consistently rather than mixing too many override slots.
- Keep seeded variation intentional and stable for the same inputs.
- Aim for assets that remain readable at native resolution and at enlarged nearest-neighbor scale.

Start from [templates/pixel_blueprint_template.py](templates/pixel_blueprint_template.py) when creating a new pixel blueprint.