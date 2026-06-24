# Session Notes — Visualization Tooling + Repo Setup

**Date:** 2026-06-24
**Time spent:** ~10:50 AM–1:15 PM (with an untracked gap early on; effective working time roughly 1.5–2 hrs)

## Goal for the session

Pick up from last session's stopping point (observer-effort distribution question parked); ended up pivoting to building the visualization layer first, plus getting the project into git/GitHub.

## What was decided, and why

- **Visualizer before further methodology work.** Compared "build the county map now" vs. "go figure out the observer-usage distribution first." Chose the visualizer — not because it's easier, but because it's infrastructure: once county data is visible, future adjustments (rare-species filtering, observer correction, season correction) become things you can toggle and see change, rather than diffing CSV rows by eye.
- **Map needs to be interactive, and able to show multiple datasets** (raw count, density, filtered versions, etc.) — not just a static image.
- **Tableau rejected** — wrong output shape for the actual destination (a plain webpage, viewable with no extra software) and a stated aesthetic dislike of its output.
- **Plotly chosen** over Folium/Bokeh/matplotlib. Reasoning: exports to a single standalone HTML file (fits the GitHub Pages destination), genuinely interactive (hover/zoom), and has a clear growth path via Dash if this becomes a multi-toggle dashboard later. Folium was the close second (arguably more visually native, built on Leaflet.js) but has clunkier per-feature popup support by default.

## What was tried / reviewed

- Reviewed the existing `main.py` (first time looking at it as a whole, not just piece by piece):
  - `get_USA_State_Counties`, `get_County_Observations`, `write_csv`, `check_bbox_area` — functioning end-to-end, with a cache-check (`if os.path.exists("colorado_counties.csv")`) that avoids re-hitting the API on every run.
  - Flagged one loose end: an "Area mismatch" print statement that currently runs unconditionally (the real `if` threshold check is commented out) — left as-is for now, not yet cleaned up.
- **Notebook detour, resolved:** considered whether Jupyter notebooks would help (separating init/expensive-steps from reprocessing) — concluded the existing cache-check in `main()` already solves that problem informally; a notebook would add format/ordering-bug overhead without solving a problem not already handled.
- **CLI staleness-check detour, named and parked:** idea to add a help blurb / flag to check cache file staleness and prompt re-download. Explicitly identified as a real but separate feature, deferred rather than started.
- **File organization decision:** discussed splitting `main.py` into multiple files (e.g. counties logic vs. species-count logic) now vs. later. Decided to defer — Plotly is brand new, the real seams in the code aren't known yet until something actually renders once. Premature splitting risks guessing wrong about where the boundaries should be.
- **Git/data hygiene, resolved through direct questions:**
  - Clarified `.venv` vs. `requirements.txt` — `.venv` is the actual local environment (never committed); `requirements.txt` is the portable recipe for recreating it (generated via `pip freeze`, does get committed).
  - Clarified `git init` vs. `.gitignore` — `git init` only creates repo machinery; `.gitignore` is a plain text file written by hand, not auto-generated. Writing it before the first commit avoids needing `git rm --cached` later to retroactively un-track things like `.venv/`.
  - Settled on a `data/raw/` vs `data/processed/` split, with a `data/README.md` to record, per file: source URL, download date, and (for processed files) which script/filter produced it.
- **Completed:** local repo organized, `.gitignore` in place, GitHub repo created.

## Open threads for next session

1. **Observer-per-person distribution** (carried over, untouched this session) — shape of observations-per-observer per county.
2. **Filter out rarely-seen species** (<5 observations threshold) — carried over.
3. **Correct for season/month** — carried over.
4. **Clean up the unconditional "Area mismatch" print** in `main.py` (the commented-out threshold check).
5. **CLI flag for cache staleness / re-download prompt** — explicitly parked, not started.
6. Generate `requirements.txt` via `pip freeze` (discussed, not confirmed done).

## Concrete next step

Confirm Plotly is installed in the venv, then get *anything* rendering — doesn't need to be real county data yet, just a working Plotly call end-to-end — before deciding whether the Plotly code deserves its own file.