# Process Notes — 7/11/26 2:45 PM – 5:54 PM

*Verification actions (doc lookups, GitHub reads, diffs) noted below as "confirmed" or "checked" were performed by Claude, not manually by Jared, unless stated otherwise.*

## Decided

- GitHub connector shows "connected" in Claude Settings but is not exposed as a callable tool in this chat. Claude checked this repeatedly via `tool_search` and `search_mcp_registry` calls, and re-checked after Jared's screenshot showed the connector as connected. Root cause not identified. Workaround: the sandbox's `bash_tool` has direct network access to `api.github.com` and `raw.githubusercontent.com` (already allow-listed), used to pull the file tree and file contents directly. This bypassed both the missing connector and `web_fetch`'s robots.txt block on `github.com` tree pages.
- Map centering fixed: changed from continental-US center (`lat 37.09, lon -95.71`, zoom 4) to Colorado (`lat 39.0, lon -105.0`, zoom 6).
- Button restyle bug fixed: buttons 2–9 used the invalid trace attribute `"color"` (a Plotly Express parameter name, not a valid `go.Choroplethmap` restyle key) instead of `"z"`. Button 2 also used `method="relayout"` (layout-only, never touches trace data) instead of `"update"`. Both fixed.
- Updatemenus `type` changed from `"dropdown"` to `"buttons"`; this caused the map render area to shrink to roughly the right half of the screen. Claude checked Plotly's `layout.updatemenus` reference and confirmed `type` only controls dropdown-vs-stacked-button rendering, not plot domain/width — so `type` itself was not the cause. Actual cause: default right-anchored `x`/`xanchor` positioning combined with 9 buttons overflowing. Fixed by setting `x=0.05, xanchor="left"`.
- `hovertemplate` line breaks: plain `\n` does not render (hover box is an SVG/HTML text layer); `<br>` used instead. Claude checked this against Plotly docs/community examples.
- `%{location}` (singular) — Claude checked this is the correct hovertemplate variable name for the location value on choropleth/choroplethmap traces, per Plotly's `hoverinfo` flaglist docs (`"location"`, `"z"`, `"text"`, `"name"`).
- `customdata` shape must be `(N points, M fields)` — built via `df[[colA, colB]].values` (stacked per row) — not a list of full column Series. The original attempt, `[df['all_species_count'], df['native_all_ratio']]`, was the wrong axis. Claude found a plotly.py GitHub issue (#3419) showing the identical mistake and the identical failure symptom (literal unresolved `%{customdata[0]}` text / placeholder shown instead of a value), confirming the diagnosis.
- Ratio columns (`native_all_ratio`, `invasive_all_ratio`) computed via `.assign()` in a new `get_county_species_ratios` function, reusing the `.replace(0, np.nan)` divide-by-zero guard already established for `native_invasive_ratio`.
- `requirements.txt` regenerated via `pip freeze`. Previous version was missing `pandas`, `numpy`, `plotly`, `requests_cache` despite all being imported in `main.py`.
- No built-in Python/Plotly attribute exists for per-feature border highlighting on hover, and no pure-Python way to handle `plotly_click`/`plotly_hover` events for a static (non-Dash) export — both require injecting custom JavaScript via `write_html(..., post_script=...)`. Decided to park both as one batched future item rather than build now.
- Switching `px.choropleth_map` → `go.Choroplethmap` would not, by itself, unlock hover-border-highlighting or click behavior — both produce the same underlying plotly.js figure, and the JS event capability is identical either way.
- CSV download split into "complete" (static file + plain `<a href>` link, no JS needed) vs. "view-specific" (needs the same `post_script` JS mechanism as the click/hover-border item). Decided to ship "complete" only for now; "view-specific" grouped with the parked JS-interactivity item.
- `fig.show()` clarified as a dev-time-only preview — it renders live but writes nothing to disk, and is unrelated to what GitHub Pages serves. The static asset needs to come from `fig.write_html(...)` or `fig.to_html(full_html=False, ...)` embedded in a hand-authored page template — this call does not exist yet in `main.py`.
- Leaning toward hand-authoring the GitHub Pages `index.html` template (rather than using Plotly's auto-generated full-HTML output), so there's a place to add the CSV download link, page title, and methodology write-up.
- Dark mode: `map_style` has a free, no-token dark option (`carto-darkmatter` / `carto-darkmatter-nolabels`), same tier as the current `carto-positron`. Noted this only darkens the map tiles — full page dark mode would additionally need `template='plotly_dark'` and fixing the hardcoded `color='black'` title font, which would otherwise conflict with a dark template.

## Tried/built

- Claude re-pulled `main.py` from GitHub mid-session and diffed it against the earlier version to confirm all of today's fixes were actually pushed and present in the live repo: `color`→`z`, `method="relayout"`→`"update"`, updatemenus `x`/`xanchor`, Colorado centering, hovertemplates 1–9 with corrected `customdata` shapes, ratio columns via `get_county_species_ratios`. Stray `from pickle import GLOBAL` and unused `import json` were also removed, unprompted.
- Dead end: assumed the GitHub connector, shown "connected" in Settings, would be directly callable. It was not, across two separate tool-search attempts and a re-check after the user's screenshot. Direct fetch of the repo tree page via `web_fetch` was also blocked (robots.txt). Resolved via the `bash_tool` network-access workaround noted above.

## Open

- `prefers-color-scheme` (OS/browser light-dark preference detection) — raised at the end of the session, not yet investigated or confirmed against current web platform behavior.
- Accessibility — named as a real concern, explicitly deferred to a 1.1/1.2 pass, no specific criteria scoped yet (WCAG level, screen-reader behavior for the map, contrast requirements all undecided).
- Button 1 vs. buttons 2–9 colorscale inconsistency (`"Blues"` vs. `"cividis"`) — not resolved. Color scheme overall stated as not yet settled; current inconsistency is functionally useful for visually confirming changes while still building out buttons/hover text.
- Default-on-load mismatch: initial `px.choropleth_map(..., color='arthropod_species_count', color_continuous_scale="Viridis", ...)` does not match button 1's declared config (`z=all_species_count`, colorscale `"Blues"`, `hoverTemplate1`), so button 1 shows as visually "active" on load without actually being what's displayed. Fix identified — apply button 1's own `args` to the figure right after creation via `fig.update_traces()`/`fig.update_layout()` — but not yet applied in code.
- GitHub connector still not directly callable in this chat despite showing "connected" in Settings. Underlying cause not identified.
- Visual gap (grey strip) between the map's right edge and the colorbar — flagged earlier in the session, not investigated.
- Import organization (grouping API / data-handling / graphing imports) — mentioned as a future task, not started.
- Unused `df` parameter in `add_county_species_counts_to_dataframe` — the function ignores its passed-in `df` and refetches via `get_county_dataframe()` internally. Not currently breaking anything since the return value is reassigned in `main()`, but flagged as a live footgun.
- "View-specific" CSV download and border-highlight/click-listener JS interactivity — parked together, not scoped beyond "will need `post_script` injection."
- No `fig.write_html()` (or equivalent static export) call exists yet in `main.py` — GitHub Pages currently has no actual artifact to serve.

## Next

Find a web page template/shell to hold the exported plot — embed `fig.to_html(full_html=False, ...)` into a hand-authored `index.html` — as the concrete starting point for the next session.