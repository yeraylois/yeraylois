# Local technology icon catalog

This directory is the offline source of truth for the dynamic stack renderer.

- `282` technology names map to `282` local SVG files in `assets/tech_icons.yml`.
- `sources.json` records the original source, resolved source, resolution method,
  and SHA-256 checksum for every asset.
- `271` entries use a recognizable upstream or previously curated logo.
- `11` entries use a deterministic geometric pictogram because no reliable
  standalone SVG could be resolved. These pictograms contain no text or badge.

Run `.github/scripts/vendor_icons.py` only when intentionally refreshing the
catalog. Normal README generation performs no icon downloads or network access.

Product names and logos remain trademarks of their respective owners. Upstream
asset licenses and usage requirements still apply; the manifest preserves the
source URL used for each file.
