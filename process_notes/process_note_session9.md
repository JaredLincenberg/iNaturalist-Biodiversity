# Process Notes — 7/5/26 5:22 PM – 7/6/26 ~4:00 PM

*Two sessions, combined at user's request: 7/5 evening build session, and a 7/6 short review session following an overnight step-back from a stuck bug.*

## Decided

- Use a **list** (`['county_id', 'taxon_id']`) rather than a tuple when calling `set_index` to build a MultiIndex. Reasoning: `set_index` treats a tuple argument as a single (possibly compound) label, not as multiple labels — so `set_index(('county_id','taxon_id'))` silently looks for one column literally named `('county_id','taxon_id')` instead of building an index from two columns.
- Deferred handling the iNaturalist API's `422` boolean-casing error (see Tried/built) to a future task, to keep momentum on the core insert/update pipeline.
- Stepped away from the pagination while-loop bug at the end of the 7/5 session rather than continuing to push through it overnight. Reasoning: returning with fresh eyes on 7/6 made the root cause (a leftover, nonsensical loop condition) fast to spot.

## Tried/built

- Confirmed `.loc[(county_id, taxon_id), column] = value` correctly inserts new rows and (pending further multi-filter testing) is expected to update existing ones, once the DataFrame's index is an actual MultiIndex on `('county_id', 'taxon_id')`. Verified via debugger output showing two rows correctly indexed and populated in `all_species_count`.
- Confirmed the DataFrame now carries all four target columns — `all_species_count`, `native_species_count`, `invasive_species_count`, `endemic_species_count` — on the `(county_id, taxon_id)` MultiIndex. `.head()` alone was misleading (the first 5 rows show only `native_species_count` populated), so nonzero data in the other two filter columns was confirmed directly via `df.invasive_species_count.sum()` and the equivalent for `endemic_species_count`.
- Confirmed via a live API response that the iNaturalist API returns a `422` with `allowedValues: ["true", "false"]` when boolean filter params (e.g. `native`) are sent capitalized (`True`/`False`) — the default string form `requests` produces from Python booleans. Not yet handled gracefully; parameters are being set manually as a workaround for now.
- Dead end (7/5 session): a `break` statement placed before the page-count check caused any single-page result set to exit the pagination loop before its data was inserted. Removed, which restored expected looping behavior across multiple pages.
- Diagnosed but not yet confirmed fixed (7/6 session): the pagination while-loop condition compared `total_pages >= 0` — likely leftover from an earlier, different version of the loop logic — instead of `total_pages >= current_page`. Correct comparison identified; application/verification of the fix not yet confirmed in this session.

## Open

- Whether the `total_pages >= current_page` fix has actually been applied and verified to produce correct pagination behavior — diagnosed, not yet confirmed working.
- Gracefully handling the API's `422` boolean-casing error (currently worked around manually, not handled in code).
- How to join iNaturalist's numeric place ID to a FIPS code or county name so the species DataFrame can match Colorado's GeoJSON county boundaries — undecided between a one-time static lookup table (64 Colorado counties, fixed set) and a programmatic per-county call to iNaturalist's places endpoint.

## Next

Apply and verify the pagination condition fix (`total_pages >= current_page`), then follow the completed DataFrame through `groupby` aggregation and produce a hardcoded map display using the existing Plotly choropleth setup — which will require resolving the iNat place ID → FIPS/county name join named above.