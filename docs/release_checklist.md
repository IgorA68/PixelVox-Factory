# Release Checklist

Use this checklist before creating the first public GitHub release.

## Scope Freeze

- Decide the first public version number.
- Confirm that both the voxel and pixel-art workflows included in the README are intended to ship in the first release.
- Avoid landing non-essential feature work during release prep.

## Automated Checks

- Confirm that the GitHub Actions workflow passes on the default branch.
- Run the local regression suite:

```bash
python -m unittest discover -s tests -v
```

## Manual Smoke Pass

- Launch `python -m vox_art.gui_launcher` and confirm the window opens.
- Launch `python -m pixel_art.gui_launcher` and confirm the window opens.
- Build at least one voxel blueprint through the CLI.
- Build at least one pixel blueprint through the CLI.
- Open at least one generated `.vox` file in MagicaVoxel.
- Confirm that README showcase assets still match the current demo set.

## Documentation Check

- Re-skim `README.md` for outdated claims.
- Confirm that linked docs and media files exist.
- Confirm that `CHANGELOG.md` reflects the user-visible changes intended for release.
- Confirm that `CONTRIBUTING.md` still matches the current workflow and scope boundaries.

## Release Metadata

- Move the intended changes out of `Unreleased` in `CHANGELOG.md` if you are cutting a versioned release.
- Create the first Git tag.
- Publish a short GitHub release summary based on the changelog.

## Nice To Have

- Add a CI badge to the README after the GitHub repository slug is final.
- Add issue and pull request templates under `.github/` if you want a more guided contribution flow.