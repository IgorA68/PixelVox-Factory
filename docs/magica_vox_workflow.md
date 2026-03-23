# MagicaVoxel And Game Asset Workflow

This repository generates `.vox` files that can be opened directly in MagicaVoxel.

## Typical Workflow

1. Pick or create a blueprint.
2. Build a `.vox` file with the GUI or CLI.
3. Open the result in MagicaVoxel.
4. Inspect silhouette, palette usage, and voxel density.
5. Adjust the blueprint code and regenerate.
6. Export the final asset from MagicaVoxel for rendering or downstream game workflows.

## Why `.vox` Output Helps

- `.vox` is the native working format for MagicaVoxel.
- Generated files can be reviewed visually without building a custom previewer.
- Palette-index output is compact and easy to iterate on from code.
- The same blueprint can generate multiple scale or seed variants for quick exploration.

## Practical Use Cases

### 1. Fast Blockout For Game Assets

Use a blueprint to generate a rough prop, vehicle, building, or terrain piece.
Then open it in MagicaVoxel and decide whether to:

- keep it as a final low-resolution stylized asset;
- repaint palette colors;
- sculpt or refine details by hand;
- export it as reference for a larger art pass.

### 2. Deterministic Variants

Seed-aware blueprints are useful when you need families of assets with predictable variation.
Examples:

- several trees with consistent style but different branch layouts;
- multiple cave chunks with the same generation logic;
- prop variants for level dressing.

### 3. Procedural Prototyping

Because the generator is just Python code, it works well for trying shape ideas quickly:

- change proportions;
- add or remove silhouette layers;
- test panel lines or structural rhythm;
- compare several seeds or dimensions.

## Recommended Iteration Loop

For most assets, the fastest loop is:

1. keep the blueprint simple;
2. lock the silhouette first;
3. only then add surface accents, lights, or small trim;
4. regenerate often instead of over-designing in one pass.

This matches how the included showcase blueprints were developed.

## Where MagicaVoxel Fits

MagicaVoxel is best treated here as the viewer, renderer, and optional manual finishing tool.
This repository handles procedural construction.

A common split is:

- blueprint code defines shape logic and repeatable structure;
- MagicaVoxel is used for previewing, rendering, palette tuning, and optional manual polish.

## Limitations To Keep In Mind

- This project currently exports `.vox` files only.
- It does not try to manage scenes, materials, or complex asset pipelines.
- It is most useful for stylized voxel assets, learning, and rapid experiments rather than full production tooling.