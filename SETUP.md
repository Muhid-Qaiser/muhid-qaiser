# Setup

Push the contents of this folder to the root of your profile repository,
`Muhid-Qaiser/muhid-qaiser`. The repository should end up as:

```text
README.md
assets/
  profile.svg    the whole profile as one image — all three sections
data/
  stats.json     collected from the GitHub API; the figures read from it
scripts/
  theme.py          palette, lettering, filters, and the document builder
  fetch_stats.py    walks the API and writes data/stats.json
  build_profile.py  composes the sections into assets/profile.svg
  section_vessel.py section_map.py section_ledger.py
.github/workflows/
  telemetry.yml  refetches and redraws the profile nightly
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
python scripts/build_profile.py   # instant: redraws assets/profile.svg
```

`build_profile.py` alone is enough after any drawing change — only
`fetch_stats.py` touches the network.

## Changing things

- **Palette and lettering** live in `scripts/theme.py`. Amber (`INFECT`) is
  reserved for a breach and is never used as decoration; keeping that rule is
  what stops the profile turning into generic neon.
- **Map areas** are keyword rules in `fetch_stats.py` (`REGIONS`), with
  hand-placed positions in `section_map.py` (`AREAS`). Each area stands in for a
  real Hallownest region — Foundations for Dirtmouth, Computer Vision for
  Greenpath, Generative AI for the City of Tears, AI Security for the Abyss —
  so its colour and position are not arbitrary. Add a repository and it lands
  in an area automatically.
- **Bloom** is what makes it read as in-game: `caps(glow=True)` picks a blur
  radius from the type size, because blurring 12px text like a 46px title
  turns it into a highlighter box rather than light.
- **One image, not three.** `document()` stacks the sections into a single SVG
  and translates each into place, so every section keeps its own local
  coordinates. Three separate images left a band of GitHub's page background
  between them; one document has no seam. The vignette is therefore drawn only
  at the outer edges — a per-section vignette would put a dark stripe at every
  join. To add a section, write a `section_*.py` exposing `H`, `svg` and
  `DEFS`, and add it to `SECTIONS` in `build_profile.py`.

## A deliberate omission

There is no lines-of-code counter. Most of these repositories are Jupyter
notebooks, whose committed JSON embeds base64 image output, so an additions
total measures the file format rather than the work — it reports over 1.7
million lines, half a million of which arrived in a single bulk commit. The
ledger counts repositories, commits and rebuilds instead, all of which survive
scrutiny.
