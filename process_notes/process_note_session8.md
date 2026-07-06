# Session — 2026-06-30

**Date:** 2026-06-30
**Time:** 1:17 PM – 6:00 PM (library)
**Focus:** DataFrame structure, query strategy, MultiIndex, debugger

## Decided

- One row per (county_id, taxon_id) with columns count_all, count_native, count_invasive, count_endemic. One-row-per-filter rejected — same taxon appears across multiple filters and endemic/native overlap isn't safe to assume.
- NaN (not zero) for unfilled count columns. Zero is semantically wrong — means "absence of data," not "zero occurrences." Would plot identically to a real count of 1, which is misleading.
- Four separate queries per county (all, native, invasive, endemic). establishment_means is sparse in response body even when API filter works correctly — iNat filters server-side but doesn't consistently echo back the field. Local filtering on response not trustworthy.
- `native` parameter requires explicit True/False, not None. Fix: build params dict conditionally, omit key entirely for "all species" query.
- MultiIndex on (county_id, taxon_id). Enables df.loc[(county_id, taxon_id), 'count_native'] = value updates without boolean mask lookups. Parquet chosen in prior session specifically because it preserves custom indexes — this session is the payoff for that choice.
- df.sort_index() required after bulk inserts before df.loc lookups — unsorted MultiIndex returns wrong results or warnings.
- VS Code debugger over print-and-fix. 64 counties × 4 filters × N species per page with variable JSON made print debugging intractable.

## Tried / built

- DataFrame.append() — AttributeError, fully removed in pandas 2.0. Replaced with list-of-dicts + pd.DataFrame.from_records(rows) once after loop.
- DataFrame join inside loop — stalled on join semantics, didn't admit confusion early enough, hoped it would resolve. Identified but not yet validated approach: pd.concat + drop_duplicates on (county_id, taxon_id) for new rows, df.loc for filling count columns.
- VS Code autocomplete reversed a < comparison — caught via debugger. Risk: autocomplete pattern-matches on code shape, not program intent. Most dangerous on moderately novel problems.
- Adams County page 1 with fields=all — establishment_means confirmed sparse. Most records don't include it even when query filter worked. Caused pivot to four-query strategy.
- iNat place page checked directly (Boulder County, taxon 40151) — noted for future use, not acted on.
- Taxon rank inconsistency noted: insects often only to genus/family, birds/plants commonly to species. Species-rank-only filter would systematically undercount poorly-documented groups. Accepted as v1 known limitation.

## Dead ends

- Local filtering on establishment_means from response — unreliable due to sparse field. Abandoned in favor of query-level filtering.
- Growing DataFrame inside loop with append — removed in pandas 2.0, replaced with list accumulation.

## Open

- Rank filtering implementation — named, not built.
- Pagination — confirmed needed, not wired in.
- df.sort_index() exact placement in loop — not yet decided.
- Loop structure not complete — debugger working, single-county validation not yet run.

## Next

Complete loop: initialize NaN row for each (county_id, taxon_id), set MultiIndex, attempt to fill count columns via df.loc per filter query (pd.concat + drop_duplicates approach identified but not yet validated). Validate on single county before full 64-county run.