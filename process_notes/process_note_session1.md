# Session Notes — Most Biodiverse Colorado County

**Date:** prior session (before 2026-06-24)
**Time spent:** not tracked at the time (process-notes habit started this session)

## Goal for the session

Answer "what is the most biodiverse location in Colorado?" using personal iNaturalist data, framed as **raw species richness by county** (decided: richness, not effort-adjusted; counties, not named regions; Research Grade observations only).

## What was decided, and why

- **Metric = raw species count**, not effort-adjusted. Simpler, and a legitimate starting metric — with the known caveat that it's biased toward heavily-observed places. Decided to carry that caveat forward rather than solve it immediately.
- **Unit = county.** Considered named regions (Front Range, Western Slope, etc.) but rejected — boundaries are fuzzy and not directly queryable. Counties are official, bounded, and iNaturalist already represents them as places.
- **Observations counted = Research Grade only.** Rejected counting all/unconfirmed observations — Research Grade means a community-confirmed ID, which is the more defensible number.

## What was tried

- Explored iNaturalist API v2 Places endpoint (`get_places`) — docs were unclear, resolved by calling the v1 autocomplete endpoint directly and inspecting real JSON responses rather than relying on prose docs.
- Identified the filter logic for "is this a CO county": `place_type == 9`, `admin_level == 20`, and Colorado's place_id (`34`) present in the place's ancestry.
- **Dead end:** tried free-text search (`q=`) to find counties by name — too noisy (78 results for "Denver" alone, mixing neighborhoods/businesses/other countries). No structured filter parameters (`place_type`, `ancestor_place_id`) exist on the search/autocomplete endpoints — confirmed by checking docs directly, not assumed.
- **Resolved via a different data source:** found and downloaded iNaturalist's official Places CSV export (linked from inaturalist.org/pages/developers), which includes `place_type`, `admin_level`, and `ancestry` as plain columns — sidesteps the fuzzy-search problem entirely.
- Verified `ancestry` is a full slash-separated lineage path (not just immediate parent) — caught and corrected a misread of the wrong column along the way.
- Verified, by checking actual rows (not just inferring from `admin_level`/`place_type` semantics), that all CO counties share the same ancestry prefix pattern (continent/USA/Colorado) before relying on it in filter code.
- Verified Denver and Broomfield (CO's city-counties) are represented as a single place entity each, not duplicated — checked directly via autocomplete rather than assumed.
- Wrote `get_us_state_counties(state_place_id)` — takes a state place_id, returns CO's 64 counties (place_type/admin_level hardcoded into the function's meaning, state passed as a parameter). Validated row count against CSV (65 lines incl. header = 64 counties — matches the real number of CO counties).
- Computed raw species richness per county. Top result: **Boulder County, 5,816 species.**

## Confounds discovered (not yet resolved)

- Calculated a "density" metric (species ÷ `bbox_area`) on a hunch that big counties would unfairly dominate. Broomfield came out "densest" — but this number was misleading:
  - `bbox_area` units are square degrees, not real area, and the distortion isn't uniform across Colorado's latitude range (confirmed via iNat forum bug report).
  - More importantly: confirmed directly (by computing the box dimensions from `swlat/swlng/nelat/nelng` myself) that `bbox_area` is the area of the **bounding box**, not the actual county polygon — so oddly-shaped counties get a distorted denominator regardless of degree-vs-real-area issues.
- **Real insight, not just a numbers artifact:** Boulder's high count likely reflects two distinct things tangled together — (1) genuine ecological diversity, since the county spans plains-to-alpine biomes, which is a real driver of species richness, and (2) observer-effort bias, since Boulder has a university and heavy outdoor-recreation culture. Area-normalizing doesn't separate these two effects — it just trades a size confound for a worse, shape-distorted one.

## Open threads for next session

1. **Shape of observations-per-person distribution** (per county) — is it long-tailed (few heavy users, many one-timers)? This is the next thread being chased, as a more honest proxy for "observer effort" than raw observer count.
2. **Filter out rarely-seen species** (e.g. <5 observations) as a noise/confidence cut.
3. **Correct for season/month** — observer activity likely isn't flat across the year; a county sampled more in peak season could look richer for effort reasons, not biology.

## Concrete next step (as of end of session)

Pick up the observations-per-person distribution question — pull (observer, observation_count) pairs per county and look at the shape.