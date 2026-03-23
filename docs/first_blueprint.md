# Your First Blueprint

This short tutorial shows the smallest useful workflow for creating a voxel blueprint. For the parallel 2D path, see [docs/pixel_blueprints.md](docs/pixel_blueprints.md).

## Step 1. Copy The Template

Start from [templates/vox_blueprint_template.py](templates/vox_blueprint_template.py).

Create a new file in `vox_blueprints/`, for example `vox_blueprints/my_crate.py`.

## Step 2. Keep The Required Contract

Every blueprint must expose:

```python
def make_model(x, y, z, W, D, H):
    ...
    return color_index_or_zero
```

The function is called once for each voxel coordinate.

- return `0` when no voxel should exist;
- return a positive integer palette index when a voxel should be written.

## Step 3. Start With One Simple Shape

Minimal example:

```python
DEFAULT_W = 48
DEFAULT_D = 48
DEFAULT_H = 48
BLUEPRINT_DISPLAY_NAME = 'Crate'
BLUEPRINT_DESCRIPTION = 'A simple boxy starter blueprint.'

from vox_art import engine as ev


def make_model(x, y, z, W, D, H):
    cx, cy = W // 2, D // 2

    if ev.is_box(x, y, z, cx - 10, cy - 10, 0, cx + 10, cy + 10, 20):
        return 120

    return 0
```

This is enough to produce a valid `.vox` model.

## Step 4. Build It

From the repository root:

```bash
python -m vox_art.build_blueprint my_crate
```

On Linux or macOS:

```bash
python3 -m vox_art.build_blueprint my_crate
```

The generated file appears in `vox_models/`.

## Step 5. Improve The Silhouette

Once the basic block works, add one change at a time.
Good first improvements are:

- a top section;
- corner trim;
- a window, vent, or accent stripe;
- a cutout or negative-space detail.

Avoid writing a complicated blueprint all at once. Iteration is the point.

## Step 6. Add Metadata

Blueprint metadata improves GUI readability:

```python
BLUEPRINT_DISPLAY_NAME = 'Crate'
BLUEPRINT_DESCRIPTION = 'A simple boxy starter blueprint.'
RECOMMENDED_W = 48
RECOMMENDED_D = 48
RECOMMENDED_H = 48
```

Recommended dimensions are optional, but useful when the blueprint looks best at a specific size.

You can also lock intended colors into the exported `.vox` file:

```python
BLUEPRINT_PALETTE_OVERRIDES = {
    120: (180, 150, 110),
}
```

That override is merged with the repository's built-in palette, so you only need to specify the slots your blueprint actually cares about.

## Step 7. Consider Seed Support Later

Only add `seed=None` when the blueprint actually benefits from deterministic variation.

That usually makes sense for:

- trees;
- rock formations;
- terrain;
- cave layouts;
- repeating prop families.

It usually does not help simple fixed props.

## Step 8. Check Before Contributing

Before proposing a new blueprint:

1. run the tests;
2. confirm the blueprint imports cleanly;
3. make sure it adds a distinct idea to the demo set;
4. keep the code readable enough for new contributors to learn from.

For repository expectations, see [CONTRIBUTING.md](CONTRIBUTING.md).