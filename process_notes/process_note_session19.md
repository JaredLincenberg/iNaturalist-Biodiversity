# Process Note — 2026-07-21 (afternoon/evening session)

**Session time:** 1:56 PM–5:53 PM.

## Decided

- Map height fix (from session 18) confirmed working — root cause was a typo (`default_height="80hv"` instead of `"80vh"`), found by comparing the working forum-code reference argument-by-argument against the broken version.
- Button layout: switched from horizontal buttons (extending right, which collided with the title) to a dropdown (extending down) — chosen as "enough to work," not a polished button system. Remaining gap (small gaps between dropdown items let hover-through reach the map underneath) named and parked as a 1.1 item, not solved now.
- Secondary-city labels at low zoom — decided **not** needed for 1.0. Diagnosed as controlled by the basemap style's own internal zoom-gated label rules, not a Plotly layout property — a real fix would mean editing vector-tile style data directly. Cost didn't match the payoff (a few extra visible city labels), so parked.
- Light/dark theme: a simple two-state switch (not independent light/dark control per page or per map) is enough for v1 — as long as it respects the OS-level `prefers-color-scheme` media query and stays architecturally decoupled enough to add per-page/per-map control later without rework.
- Theme architecture: chosen mechanism is a DOM attribute (`data-bs-theme` on `<html>`) watched via `MutationObserver` — not a plain JS variable (no built-in listener mechanism exists for a bare variable reassignment) and not one tangled function that both sets the DOM attribute and calls `Plotly.relayout()` directly.
- With ~20 minutes left near session end, decided to spend it on the theme refresh-flash fix first (small, bounded), then start C5 (color axis) if time allowed. In practice, remaining time went entirely to the flash-fix discussion — C5 was not started.

## Tried / built

- Bootstrap-native light/dark toggle: built and confirmed working, respecting `prefers-color-scheme` via Bootstrap's own documented color-modes script (checks `localStorage`, falls back to `matchMedia`).
- Map theme listener: `MutationObserver` on `document.documentElement`, filtered to `data-bs-theme` via `attributeFilter` (avoids firing on unrelated attribute changes). Confirmed the target node is `document.documentElement`, matching what the slider script itself already calls `.setAttribute()` on — no separate query/lookup needed.
- `paper_bgcolor` identified as the correct property for margin color (not `plot_bgcolor`, which governs the area between cartesian axes — not very meaningful for a `choropleth_map` with no traditional axes). Confirmed why it's `paper_bgcolor` (flat, underscore) rather than `paper.bgcolor` (dotted): `font` is a real nested object with documented sub-properties (`color`, `family`, `size`); `paper` isn't — `paper_bgcolor` is one flat, self-contained property name.
- Jinja structuring for shared vs. page-specific scripts: universal script (theme slider) placed directly in `base.html`'s body, outside any block, to avoid the `{% block %}` override/`super()` footgun; a separate empty `{% block extra_scripts %}` added for optional per-page scripts (e.g., the map listener), left undefined on non-map pages. Per-page behavioral differences intended to be handled via small inline config passed to a generic reusable JS function, not via different Jinja logic per page.
- Refresh-flash bug diagnosed: on reload, if dark mode was already saved, the toggle UI reads the stored value correctly and displays right away, but the map stays stale — because `MutationObserver` only reports changes occurring after `.observe()` is called, not the already-existing state at attach time. Fix pattern identified: call the same theme-apply function once on `DOMContentLoaded` (not `window.onload`, which waits on images/stylesheets unnecessarily) in addition to the observer's callback — two call sites, one function. Wiring pattern given; implementation/confirmation status at session end unclear — additional, unspecified theme-setting issues were reported right as the session ended.

## Open

- **Listener issue:** additional theme-setting issues surfaced after the `DOMContentLoaded` fix pattern was discussed; specifics weren't detailed before the session ended.
- **C5 (color axis initialization):** still fully open — planned for this session's remaining time but never actually started.

## Next

- Pin down and resolve whatever theme-setting issues remain with the listener (specifics TBD at next session's start).
- Scope and begin C5: decide the initial colorscale state/behavior across metrics as an actual decision to make, not a bug to fix.

## Process/tooling notes

- (none this session)