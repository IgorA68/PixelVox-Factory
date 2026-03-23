# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog and is intentionally lightweight for this repository.

## [Unreleased]

### Added

- New pixel-art geometry helpers: `is_line(...)`, `is_polyline(...)`, `is_polygon(...)`, `is_rect_outline(...)`, `is_circle_outline(...)`, `is_ellipse_outline(...)`, `is_diamond_outline(...)`, and `is_polygon_outline(...)` for contours, panel borders, ring-like shapes, and irregular silhouettes.
- Procedural pixel-art runtime via [pixel_art/engine.py](pixel_art/engine.py) with a separate internal [pixel_engine/](pixel_engine) implementation layer.
- Dedicated pixel blueprint loading, validation, metadata, and seed-handling utilities via [pixel_art/blueprint_utils.py](pixel_art/blueprint_utils.py).
- A CLI entry point for procedural pixel-art export through [pixel_art/build_blueprint.py](pixel_art/build_blueprint.py).
- A batch CLI entry point for regenerating the curated pixel-art showcase set through [pixel_art/build_demo_assets.py](pixel_art/build_demo_assets.py).
- A separate pixel-art GUI launcher through [pixel_art/gui_launcher.py](pixel_art/gui_launcher.py), with single-build, output-folder, and showcase-batch controls.
- A first seed-aware pixel blueprint smoke example in [pixel_blueprints/gem_icon.py](pixel_blueprints/gem_icon.py).
- A first practical pixel-art demo set with [pixel_blueprints/potion_icon.py](pixel_blueprints/potion_icon.py), [pixel_blueprints/grass_tile.py](pixel_blueprints/grass_tile.py), [pixel_blueprints/crate_prop.py](pixel_blueprints/crate_prop.py), [pixel_blueprints/bush_prop.py](pixel_blueprints/bush_prop.py), [pixel_blueprints/stone_floor_tile.py](pixel_blueprints/stone_floor_tile.py), and [pixel_blueprints/tiny_face_avatar.py](pixel_blueprints/tiny_face_avatar.py).
- Pixel-art documentation and authoring guidance in [docs/pixel_blueprints.md](docs/pixel_blueprints.md), plus README and contributor updates for the new 2D workflow.
- Curated reusable pixel-art palette presets in [pixel_art/palettes.py](pixel_art/palettes.py).
- A dedicated pixel blueprint template in [templates/pixel_blueprint_template.py](templates/pixel_blueprint_template.py).
- Regression coverage for pixel geometry helpers, PNG export behavior, palette overrides, seed determinism, and pixel blueprint contracts.
- Embedded palette support for `.vox` export, aligned to MagicaVoxel `pal0`, with optional per-blueprint overrides.
- PNG preview export alongside `.vox` generation, with orthographic, top, isometric, and combined preview modes.
- Preview-only build mode for generating PNG output without rewriting `.vox` files.
- Optional `output_dir` support for public `.vox` export calls and the CLI build path.
- Optional `--quiet` CLI support and `progress=False` API controls for `.vox` export, preview generation, and batch preview builds.
- Batch showcase preview generation through `python -m vox_art.build_preview_assets` and the shared CLI build pipeline.
- GUI controls for preview generation, preview mode selection, preview scale, and preview-only output.
- Persistent GUI state for preview-related fields, including preview mode, preview scale, and preview toggles.
- README positioning for the project as a procedural voxel generator, AI imagination sandbox, and human-AI co-creation playground.
- Documentation for MagicaVoxel workflow integration in [docs/magica_vox_workflow.md](docs/magica_vox_workflow.md).
- A first blueprint tutorial in [docs/first_blueprint.md](docs/first_blueprint.md).
- Technique-oriented examples: [vox_blueprints/primitive_layers.py](vox_blueprints/primitive_layers.py) and [vox_blueprints/negative_space_arch.py](vox_blueprints/negative_space_arch.py).
- Blueprint metadata support and deterministic seed support for compatible blueprints.
- Contributor-facing template and guidance for new blueprints.

### Changed

- The repository now has a separate `images/` output path for procedural pixel-art PNG exports, instead of mixing them into voxel output under `vox_models/`.
- Voxel-facing public entry points now live under the packaged `vox_art/` surface instead of root-level helper scripts, bringing the voxel layout in line with the packaged pixel-art surface.
- The exporter now writes an embedded palette aligned with MagicaVoxel `pal0`, so palette indices stay stable across viewers.
- `vox_art/engine.py` now acts as a stable public facade over the internal `vox_engine/` modules, so the runtime can grow without breaking existing blueprint imports.
- The CLI build path now reuses one voxel build for `.vox` and preview export instead of evaluating the blueprint twice.
- The CLI can now direct `.vox` output to a custom target directory while keeping preview output independently configurable.
- Batch and scripted workflows can now suppress progress output for cleaner logs without changing generated files, whether through CLI `--quiet` or API-level `progress=False`.
- Preview PNG filenames now include the selected mode suffix, such as `house-isometric.png` or `hills-top.png`, so multiple preview variants do not overwrite each other.
- Preview generation now auto-clamps the effective scale for large models to keep PNG output within a reasonable maximum size.
- Terrain-style models can now use a compact top-view preview instead of a wide orthographic contact sheet.
- Showcase blueprints were recalibrated against `pal0` so their default appearance is more coherent in MagicaVoxel.
- GUI workflow no longer rewrites blueprint source files when dimensions change.
- GUI and CLI now share centralized blueprint loading and validation helpers.
- GUI output affordances now make it clearer that the output folder contains both `.vox` files and preview PNGs.
- README now emphasizes practical co-creation, rapid iteration, and clear project boundaries.
- README now includes a small showcase gallery backed by committed preview assets instead of describing screenshots as future work.
- Preview documentation, screenshot planning, and publication asset guidance now distinguish autogenerated technical previews from final MagicaVoxel README screenshots.
- The curated demo set now includes more distinct showcase examples and technique-oriented learning material.
- CONTRIBUTING now includes stronger release-stage guidance for scope control, media updates, smoke checks, and repository-facing documentation changes.

### Fixed

- Portable launcher behavior on Windows when a preferred Python launcher is unavailable.
- Windows preview logging now tolerates output directories on different drive letters without failing on `relpath`.
- Preview-only GUI state can no longer remain enabled when PNG preview output itself is disabled.
- Extremely large preview images for big models such as `hills` are now automatically reduced to practical sizes.
- Clearer import and validation error handling in the GUI.
- Vehicle showcase geometry and polish issues in the current demo set.

### Internal

- Added regression tests for geometry helpers, blueprint contracts, validation behavior, seeded blueprint determinism, preview rendering modes, adaptive preview scaling, and preview filename conventions.
- Added regression coverage for custom `.vox` output directories and silent export / preview execution.
- Split engine internals into dedicated voxel-building, geometry, `.vox` export, and preview modules under `vox_engine/` while keeping `vox_art/engine.py` as the compatibility layer.
- Removed the obsolete root voxel facade and builder scripts after repointing blueprints, tests, docs, and launchers to `vox_art/`.
- Refactored `vox_art/engine.py` toward a more explicit and test-backed runtime contract.
