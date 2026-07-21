# Process Note — 2026-07-19 (afternoon session)

**Session time:** 1:43–2:59 PM.

## Decided

- **Bootstrap chosen over Pico.css/Tailwind for site styling.** Split "configurable menus/headers/footers" from "basic design" — the former is Jinja template inheritance (`{% extends %}`/`{% block %}`), a tool already in use, not new tech. The latter needed an actual CSS framework. Bootstrap picked because the ask was specifically for *configurable* nav/footer, and Bootstrap gives named, documented components to configure rather than Pico's automatic classless styling. Tailwind's CDN build ruled out — its own docs say it's explicitly dev-only, not meant for a live production page.
- **Nav links deferred — map only for v1.** Consistent with the existing scope-discipline pattern (C5, parked density function): name it and park it rather than build for pages that don't exist yet. Practical result: placeholder nav-item `<li>`s to be dropped from the navbar, keeping just the brand/site name; the toggler markup can stay since it's harmless sitting empty.
- **Light/dark theme toggle is a v1 requirement, not v1.1.** Jared's own words: "something I want to do before done."

## Tried / built

- **GitHub Pages enabled and live.** Repo check at session start: `docs/index.html` was already wired — `main.py` already writes the rendered Jinja template there (lines 476–478) — but GitHub Pages itself wasn't turned on (404 from the Pages API). Walked through Settings → Pages → Deploy from branch (main/docs). Jared reported the page live afterward; not independently re-verified via API this session.
- **`base.html` + `index.html` built via Jinja inheritance, Bootstrap 5.3.8 (CDN, CSS+JS bundle with SRI hashes).** Confirmed working by Jared.
- **Light/dark theme diagnosed as three independent, non-syncing layers**, not one: (1) Bootstrap `data-bs-theme` — page chrome only (navbar/footer/body); (2) Plotly figure chrome (`paper_bgcolor`, `font.color`) — baked in server-side when `main.py` builds the figure; (3) MapLibre base-map tile style (`layout.map.style`, specific to `choropleth_map`). None sync automatically — toggling Bootstrap's theme touches only (1). If a live toggle gets built: same JS mechanism already used for the colorscale dropdown (`Plotly.relayout()` on an event), just targeting `map.style`/`paper_bgcolor`/`font.color` instead of `coloraxis.colorscale`. Not yet built.
- **Map height bug (450px) diagnosed; fix identified, not yet applied.** Initial theory: CSS percentage-height collapsing up an unbroken ancestor chain (every parent needs an explicit height for `%` to resolve). Refined once Jared pulled Plotly's own reference docs directly: `layout.height` defaults to 450px and `layout.width` to 700px as static values — the simpler, more direct root cause, confirmed independently via Plotly's official interactive-html-export docs and a live matching GitHub issue (plotly.py #5591 — same symptom, locked at 450px despite responsive CSS around it). Fix needs three pieces together: `fig.update_layout(autosize=True, height=None)` in the figure-building code; `config={"responsive": True}` passed to `fig.to_html()`; `default_height="80vh"` (placeholder value, not yet chosen by Jared) also passed to `fig.to_html()` — this last one is what actually resolves the original bug, replacing the div's plain `100%` inline style (needs a resolvable ancestor chain) with a viewport-relative unit that doesn't.

## Open

- Light/dark toggle not yet built — diagnosis done, implementation is next-session work.
- Map height/responsive fix not yet applied to `main.py`.
- Nav links intentionally deferred — write-up page and about page were the two options considered and both declined for now; candidate for a later version if revisited.

## Next

Apply the three-piece height fix to `main.py` (`autosize=True, height=None` on the figure; `config={"responsive": True}` and `default_height="80vh"` on `fig.to_html()`), confirm in-browser that the map fills its container correctly, then move to building the light/dark toggle (Bootstrap toggle button wired to `Plotly.relayout()`, same pattern as the colorscale dropdown).

## Process/tooling notes
- GitHub's unauthenticated `contents`/`commits` API hit its rate limit mid-session. Fell back to a `codeload.github.com` tarball download to inspect repo structure, which isn't subject to the same limit. Worth considering an authenticated token if this keeps recurring — consistent with the standing GitHub-API-workaround note.