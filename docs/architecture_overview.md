# Architecture Overview

This repository stays intentionally small, but it now has a clearer split between public API, workflow entry points, and internal engine logic across both the voxel and pixel-art surfaces.

## Main Roles

- `vox_art/engine.py`: stable public facade used by blueprints, tests, CLI, and GUI.
- `vox_engine/`: internal implementation modules for voxel collection, preview rendering, geometry helpers, and `.vox` writing.
- `vox_art/build_blueprint.py`: CLI workflow for building one voxel blueprint or a curated batch of previews.
- `vox_art/gui_launcher.py`: Tkinter workflow for interactive voxel builds.
- `vox_art/blueprint_utils.py`: voxel blueprint discovery, loading, validation, metadata, and fill-function adaptation.
- `pixel_art/engine.py`: stable public 2D facade used by pixel blueprints, tests, CLI, and GUI.
- `pixel_engine/`: internal implementation modules for pixel collection, geometry helpers, palette handling, and PNG writing.
- `pixel_art/build_blueprint.py`: CLI workflow for building one pixel-art blueprint.
- `pixel_art/build_demo_assets.py`: batch CLI workflow for regenerating the curated pixel-art showcase set.
- `pixel_art/gui_launcher.py`: Tkinter workflow for interactive pixel-art builds.
- `pixel_art/blueprint_utils.py`: pixel blueprint discovery, loading, validation, metadata, and fill-function adaptation.

## Public Engine Contract

Blueprints should continue importing the public voxel facade directly:

```python
from vox_art import engine as ev
```

The public surface is intentionally small:

- geometry helpers such as `is_sphere(...)`, `is_cylinder(...)`, and `is_box(...)`;
- `save_as_vox(...)` for `.vox` export, including optional `output_dir` and `progress=False` control;
- `save_preview_png(...)` for standalone preview generation, including optional `progress=False` control;
- `save_outputs(...)` for one-pass export of `.vox` and preview outputs from a single voxel build, including shared `progress=False` control and `.vox` output routing.

The key compatibility rule is simple: internal modules may change, but external callers should not need to stop importing `vox_art.engine`.

Pixel blueprints follow the same rule on the 2D side:

```python
from pixel_art import engine as ep
```

The current pixel-facing public surface stays intentionally small as well:

- geometry helpers such as `is_rect(...)`, `is_circle(...)`, `is_ellipse(...)`, and `is_diamond(...)`;
- `save_as_png(...)` for PNG export with optional output routing, palette overrides, scaling, and `progress=False` control.

As with the voxel side, internal 2D modules may change, but external callers should not need to stop importing `pixel_art.engine`.

## Internal Engine Split

The `vox_engine/` folder separates concerns that had started to accumulate inside the public voxel facade:

- `vox_engine/core.py`: input validation, color normalization, progress output, and voxel collection.
- `vox_engine/geometry.py`: reusable shape predicates and measure validation.
- `vox_engine/export.py`: `.vox` payload creation and writer integration.
- `vox_engine/preview.py`: orthographic, top, isometric, and combined PNG preview rendering.

This split keeps the facade stable while reducing the chance that preview work accidentally destabilizes blueprint-facing helpers.

The `pixel_engine/` folder does the same for 2D output:

- `pixel_engine/core.py`: input validation, color normalization, progress output, and pixel collection.
- `pixel_engine/geometry.py`: reusable 2D shape predicates.
- `pixel_engine/export.py`: PNG payload creation and image writing.

This keeps the 2D facade small and avoids coupling pixel-art changes to the voxel runtime.

## Build Flow

The current voxel build flow is:

1. `vox_art.build_blueprint` or `vox_art.gui_launcher` resolves a blueprint module through `vox_art.blueprint_utils`.
2. The blueprint is converted into a runtime `fill_func(x, y, z, W, D, H)`.
3. `vox_art.engine.save_outputs(...)` builds the voxel list once.
4. The same voxel list is reused for `.vox` export and optional PNG preview export.

That last step is the main architectural improvement from the recent refactor: the CLI path no longer evaluates the same blueprint twice when both `.vox` and PNG outputs are requested.

At the workflow level, the CLI flag `--quiet` maps onto the engine-level `progress=False` behavior.

The pixel-art flow mirrors the same idea in 2D:

1. `pixel_art.build_blueprint` or `pixel_art.gui_launcher` resolves a blueprint module through `pixel_art.blueprint_utils`.
2. The blueprint is converted into a runtime `fill_func(x, y, W, H)`.
3. `pixel_art.engine.save_as_png(...)` evaluates the blueprint and writes the final PNG.

The two surfaces intentionally share metadata and seeding conventions while keeping their runtime contracts separate.

## Why The Facade Matters

Most blueprints import `vox_art.engine` directly, and tests also reference helper functions from that module. Replacing the facade with direct internal imports would make future refactors much riskier.

Keeping stable public package surfaces gives the project these benefits:

- blueprints remain simple and readable;
- tests can validate a clear public engine contract per surface;
- internal preview/export refactors stay isolated;
- future API growth can be staged behind one compatibility layer per mode.

## Near-Term Extension Points

The current structure makes a few future changes safer:

- additional output-routing options built on top of the existing public `output_dir` support for `.vox` export;
- more granular logging controls beyond the current `progress=False` behavior;
- additional preview renderers or export adapters;
- additional PNG export options or shared palette tooling on the pixel-art side;
- higher-level composition helpers built on top of existing geometry primitives.

The recommended rule is to add new behavior to `vox_engine/` first, then expose it through `vox_art.engine` only when the public contract is clear.