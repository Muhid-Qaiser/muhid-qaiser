# Setup

Push the contents of this folder to the root of your profile repository,
`Muhid-Qaiser/muhid-qaiser`. The repository should end up as:

```text
README.md
assets/          vessel · map · ledger · bench · shop (all SVG)
data/
  stats.json     collected from the GitHub API; the figures read from it
scripts/
  theme.py         palette, lettering, ink and glow filters — edit here first
  fetch_stats.py   walks the API and writes data/stats.json
  build_map.py     redraws assets/map.svg
  build_ledger.py  redraws assets/ledger.svg
  build_vessel.py  build_bench.py  build_shop.py
.github/workflows/
  telemetry.yml  refetches and redraws the map and ledger nightly
```

## After pushing

1. Open the **Actions** tab and enable workflows if GitHub asks.
2. Run **Redraw the map** once, or wait for the 03:23 UTC schedule.

No personal access token is needed — the workflow uses the built-in
`GITHUB_TOKEN`. If branch protection blocks the bot from pushing to `main`,
allow GitHub Actions to write to the branch.

## Redrawing locally

```bash
export GITHUB_TOKEN=$(gh auth token)
python scripts/fetch_stats.py     # ~2 min: walks every repository
python scripts/build_map.py
python scripts/build_ledger.py
```

The vessel, bench and shop are hand-authored art and do not depend on the
API — rebuild them only when you change the copy or the drawing.

## Changing things

- **Palette and lettering** live in `scripts/theme.py`. Amber (`INFECT`) is
  reserved for a breach and is never used as decoration; keeping that rule is
  what stops the profile turning into generic neon.
- **Map areas** are keyword rules in `fetch_stats.py` (`REGIONS`), with
  hand-placed positions in `build_map.py` (`AREAS`). Each area stands in for a
  real Hallownest region — Foundations for Dirtmouth, Computer Vision for
  Greenpath, Generative AI for the City of Tears, AI Security for the Abyss —
  so its colour and position are not arbitrary. Add a repository and it lands
  in an area automatically.
- **Shop wares** are a plain list at the top of `build_shop.py`.
- **Bloom** is the thing that makes it read as in-game: `caps(glow=True)` picks
  a blur radius from the type size, because blurring 12px text like a 46px
  title turns it into a highlighter box rather than light.

## A deliberate omission

There is no lines-of-code counter. Most of these repositories are Jupyter
notebooks, whose committed JSON embeds base64 image output, so an additions
total measures the file format rather than the work — it reports over 1.7
million lines, half a million of which arrived in a single bulk commit. The
ledger counts repositories, commits and rebuilds instead, all of which survive
scrutiny.
