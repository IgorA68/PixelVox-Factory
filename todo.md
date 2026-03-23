# Roadmap

This file now tracks active work only.

Completed milestones for the current voxel pipeline already live in the codebase, README, changelog, tests, and docs. The roadmap below keeps only the remaining voxel follow-ups plus the new pixel-art expansion.

## Current Focus

1. Keep both the voxel and pixel-art workflows stable while preparing the first public release.
2. Keep public commands, docs, templates, and contributor guidance aligned with the packaged `vox_art/` and `pixel_art/` surfaces.
3. Reuse the existing procedural blueprint idea instead of turning the repository into a general illustration generator.

Out of scope for now: anime illustration generation, freeform painting workflows, and non-voxel/non-pixel-art rendering experiments.

## Voxel Release Follow-Ups

- [x] Add 3-5 strong screenshots or GIF previews for the generated voxel models.
- [x] Expand contribution guidelines after the first public feedback cycle.

Status note: the voxel build path, GUI flow, preview rendering, metadata support, seed support, palette overrides, packaged `vox_art/` facade, and internal engine split are already in place and should now be treated as the stable baseline.

Release note: the first public tag should be created only when the intended public scope is complete. If pixel art is part of the first real release, tagging waits until the pixel-art baseline is also ready.

## Voxel Engine Follow-Ups

- [ ] Add blueprint composition helpers for combining primitives at a higher level.
- [ ] Add a regression test for progress helper behavior only if the helper grows beyond its current simple form.
- [ ] Explore export adapters beyond `.vox` only if real user demand appears.

Rule: avoid expanding the voxel engine in ways that blur the current simple public contract unless there is a concrete workflow need.

## Pixel Art Expansion

### Stage 1. 2D Architecture

- [x] Define a dedicated 2D blueprint contract for procedural pixel output.
- [x] Decide how much of `vox_art.blueprint_utils` metadata and seed handling should be shared between voxel and pixel blueprints.
- [x] Add a separate image engine module instead of forcing 2D output through the voxel engine.
- [x] Keep palette-based rendering as a first-class constraint for the pixel-art path.

Current decision: keep voxel and pixel blueprint loading separate for now through dedicated utility modules, while preserving the same metadata style, seed semantics, and palette override model across both modes.

### Stage 2. Rendering And Export

- [x] Add PNG export for pixel-art blueprints as a primary output, not just as a voxel preview.
- [x] Support nearest-neighbor scaling for clean enlarged exports.
- [x] Add optional background, transparency, and palette override controls for 2D output.
- [x] Decide whether generated files live in `vox_models/`, a new `images/` folder, or per-mode output folders.

Current decision: pixel-art PNG output now goes to `images/` by default so it stays clearly separated from voxel models in `vox_models/`.

### Stage 3. Workflow Integration

- [x] Add a CLI entry point for pixel-art blueprint builds.
- [x] Add a batch CLI path for regenerating the curated pixel-art demo set.
- [x] Decide whether the GUI gets a mode switch for voxel vs pixel-art generation or stays voxel-only until the 2D path is stable.
- [x] Keep deterministic seed support for pixel-art blueprints where it adds real value.
- [x] Keep discovery, validation, and error messages consistent with the existing voxel workflow.

Current decision: keep the voxel GUI separate and add a dedicated pixel-art launcher instead of forcing both workflows into one window too early.

### Stage 4. First Demo Set

- [x] Add 3-5 showcase pixel-art blueprints.
- [x] Include at least one icon-scale asset, one tile or terrain example, one prop, and one simple character or portrait-style generator.
- [x] Add a small curated palette set suitable for pixel-art outputs.
- [x] Verify that the demo set is readable both at native resolution and at enlarged export scale.

Current demo set: `gem_icon`, `potion_icon`, `grass_tile`, `crate_prop`, `bush_prop`, `stone_floor_tile`, and `tiny_face_avatar`. The set now covers UI items, terrain, props, simple foliage, floor tiles, and an NPC/avatar placeholder workflow.

### Stage 5. Documentation And Tests

- [x] Document the pixel-art blueprint contract with one minimal example and one layered example.
- [x] Explain how the pixel-art path relates to the existing voxel workflow and where the boundaries are.
- [x] Add tests for blueprint loading, seed handling, palette mapping, and basic image output dimensions.
- [x] Add contributor guidance for creating new pixel-art blueprints.

Current documentation: pixel-art contract and examples now live in `docs/pixel_blueprints.md`, while README and CONTRIBUTING both describe the pixel path as a CLI-first procedural blueprint workflow parallel to the voxel system.

### Stage 6. Publication Readiness

- [ ] Decide the first public release version once the voxel and pixel-art scope is frozen.
- [ ] Add release tags for the first public release.
- [ ] Do a final smoke pass across voxel and pixel-art entry points before publication.

## Later Pixel-Art Steps

### Separate Pixel GUI

- [x] Add a dedicated pixel-art GUI launcher built around the existing single-build and batch-build CLI paths.
- [x] Keep pixel GUI state separate from voxel GUI state.
- [x] Expose output name, seed, scale, and batch showcase generation from the pixel GUI.
- [ ] Only revisit a unified GUI after both launchers prove stable on their own.

Current decision: `pixel_art.gui_launcher` now handles the flat pixel-art workflow with its own state file and controls. Keep it separate from the voxel launcher until real usage shows that a unified GUI would actually reduce friction.

### Isometric Pixel Path

- [ ] Define a separate isometric pixel-art track instead of treating it as a flag on the flat 2D blueprint path.
- [ ] Design a small set of isometric helper primitives for AI-authored blueprints.
- [ ] Add first isometric showcase assets such as tree, crate, and stone block.
- [ ] Decide later whether isometric assets belong in the same pixel GUI or in a separate isometric mode.

## Recommended Order

1. Keep the voxel and pixel-art baselines stable while final publication tasks are completed.
2. Run one final smoke pass across both packaged CLI and GUI entry points.
3. Freeze the public scope, choose the release version, and only then create the first tag.

## Decision Notes

- Keep the repository focused on procedural blueprints for voxel models and pixel art.
- Do not expand into anime illustration generation in this repository.
- Prefer one shared project only while the two modes still benefit from the same procedural philosophy, metadata model, and contributor workflow.
- If the 2D branch later grows into a much broader illustration system, split it into a separate project instead of diluting the current scope.
- Do not create the first public release tag before the intended pixel-art baseline is actually included, if pixel art remains part of the promised scope.