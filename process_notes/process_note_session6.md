# Session — 2026-06-27 (Part 2)

**Time:** ~6:50 PM to 10:35 PM
**Focus:** requests-cache integration, iNaturalist `fields`/RISON and taxon data, table structure design, type bug discovery

## Decided

- Chose `requests-cache` over hand-building a caching layer. Reasoning: separated "what to build" from "what would be interesting to study" — using the library now doesn't preclude reading its source or building a toy version later purely to learn from it. Don't need to choose only one.
- Confirmed `requests-cache` builds cache keys from the full request (URL + params together), not just URL — so different filter combinations are automatically treated as distinct cache entries. This was the actual mechanism behind the original "does it handle param comparison" question.
- Resolved the "is it actually caching or still pinging the server" uncertainty with a concrete, checkable test: `response.from_cache` (True/False) on repeated calls, rather than trusting it blindly.
- Resolved the sleep/rate-limit question by tying it directly to that same check: only sleep when `from_cache` is False, since a cache hit never touches the server. Removes the ambiguity instead of guessing "probably fine."
- Found the `ttl` parameter listed in iNaturalist's own v2 API docs; searched the `pyinaturalist` (third-party Python wrapper) docs for a more detailed explanation of what it does, which confirmed it sets the `Cache-Control` HTTP header (max-age, in seconds). Conclusion: not a separate caching system to build against — `requests-cache` with `cache_control=True` already reads `Cache-Control` headers automatically. One less thing to build.
- Distinguished application-state staleness (the kind handled by force-reset flags at a past job — multiple live systems needing to agree *right now*) from external-API staleness (slow-moving, low-stakes, a stale cache just means missing a recent observation by hours/days). Concluded `timedelta`-based expiration is a fine fit for this project; a manual force-reset escape hatch is easy to add later if ever needed, but not necessary now.
- **Table structure decided:** taxon reference dataframe (global, static facts — name, rank, etc.) separate from a county-presence dataframe (taxon ID + county, holding place-scoped facts like `establishment_means`/native status). Originally proposed as three tables; corrected back down to two after directly checking the actual API response shape — `establishment_means` is already a single object combining taxon + place + status, confirming it belongs in the county-presence table rather than needing its own separate structure.

## What was tried / built

- Looked into the iNaturalist API's default minimal response behavior: by default, most endpoints return only a minimal identifier (taxon ID is serial, not a UUID); full data (including nested objects like `taxon`) requires the `fields` parameter. Learned this is why the taxon object had seemed inaccessible — it wasn't missing, just gated behind a parameter not yet being used.
- Learned `fields` for nested objects (like `taxon`) requires RISON syntax (URL-friendly JSON variant), not a simple comma-separated list — flagged as genuinely new syntax to learn, not just "another parameter." `fields=all` noted as a way to see the full available shape before committing to specific fields.
- Used `fields=all` and found a real example of place-scoped taxon data directly in the response: an `establishment_means` object containing `establishment_means: 'introduced'`, plus a nested `place` object (id, name, ancestry) — concrete evidence that native/introduced status is tied to a specific place, not a global taxon property. This directly informed the two-table design above.
- Confirmed pagination has no new conceptual complexity — same call, different `page` number, looped. The real open question correctly identified as downstream of that: storage and processing of the combined results, not the pagination mechanism itself.
- Raised, then set aside without resolving tonight: whether stacking/batching multiple taxon ID queries together (vs. one call per ID) is worth the API-call savings, given it breaks the otherwise-clean one-ID-per-cache-entry reuse. Taxon facts (name, rank) are highly stable, so per-ID caching essentially lasts forever — tradeoff not settled, just named.
- **Found a real bug while building from scratch:** species count came through from JSON as a string (not an int) when rebuilding the pipeline from the ground up, despite an earlier dataframe (built differently) having had it correctly typed as int. The string-typed column got treated as categorical/label data instead of a continuous value, breaking the intended color-range mapping on the map (discrete buckets instead of a gradient). Root cause: JSON doesn't enforce numeric typing the way a dataframe might assume, so a count can serialize as `"42"` instead of `42`, and pandas won't complain either way.

## Reflection

This bug directly reinforced the earlier reasoning about choosing structured code over Jupyter notebooks: in a notebook, an old correctly-typed dataframe could persist across cell reruns even after the underlying logic changed, silently hiding this exact failure mode. Rebuilding from scratch (forced by the code-file structure, not notebook cells) surfaced the actual current behavior instead of stale in-memory state masking it. Named explicitly as a useful general principle, not just a one-off bug: **type assumptions silently break when state isn't rebuilt from scratch.**

Also discussed directly: the value of concrete, specific examples (like this bug) over "vibes" when eventually writing this up — specifics are checkable and arguable in a way vibes aren't. Counterpoint also raised and agreed with: specificity alone isn't automatically honest either — a cherry-picked specific example used to win a pre-decided argument is just dogma in concrete's clothing. What makes tonight's examples useful isn't that they're specific, it's that they were found while looking for something else, not planted to prove a point decided in advance.

Session assessment, in own words: more wandering than the first part of tonight, less linear progress than hoped, but satisfied that the complexity being surfaced and worked through will lead to real progress — not wasted motion, even though it didn't feel like forward momentum step by step.

## Open questions / not yet started

- Taxon ID batching vs. per-ID caching tradeoff — named, not resolved.
- Pagination storage/processing implementation — conceptually scoped (loop + combine into the two-table structure) but not yet built.
- Need to verify whether `establishment_means`/native status is reliably available across all observations/counties, or only sometimes present.
- The string/int type bug needs an actual fix (explicit type casting on load) — found tonight, not yet patched.

## Concrete next step

Fix the species-count type bug (explicit cast to int on load from JSON) before doing anything else with that column. Then implement the two-table structure (taxon reference + county-presence) and wire up pagination to populate it.