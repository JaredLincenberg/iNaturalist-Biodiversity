# Process Note — 2026-07-09

**Time:** 4:08 PM–5:06 PM (stated hard stop at 5:00 for a 6:30 PM commitment; session ran to 5:06 to save two output images and write this note)

## Decided

- Build a dedicated taxon-level dataframe (keyed by `taxon_id`), rather than issuing separate API filter calls for each of the six group options. Reasoning: faster to run, kinder to iNat's API load, and comparing two dataframes against each other (taxon-level vs. county-level) was expected to surface more learning than six flat filtered pulls.
- Skip a separate statewide Colorado species API request. Reasoning: taxonomic metadata (`iconic_taxon_name`, ancestry path) is already present in the existing per-county API calls and had simply been ignored until now — a separate request would be redundant.
- Use ancestry-ID path matching (not `iconic_taxon_name` alone) to classify Vertebrates. Reasoning: `iconic_taxon_name` only returns the lowest-level tag a taxon has (e.g. Insecta, not Animalia), so some vertebrate classes without their own iconic tag would be missed by a simple union of iconic_taxon_name values.
- Store both `iconic_taxon_name` and the ancestry path on the taxon dataframe, and use ancestry-path matching for now. Reasoning: both fields are already in the API response at no extra cost, and keeping both preserves the option to fall back to simpler iconic_taxon_name unions later if the Colorado-specific edge case (vertebrate classes with no dedicated iconic tag) turns out to be negligible.
- Of the six group options (Native, Invasive, Flora, Fauna, Flora+Fauna, Vertebrates), only Flora+Fauna needs OR/union logic; the other five are single-condition filters.
- Native/invasive ratio color scale: floor the range at 0, no log transform, for Phase 1. Reasoning: a log-scaled color axis was tried previously and abandoned (hover values and legend stopped matching the underlying data meaningfully); a well-chosen color scheme plus a 0 floor was judged sufficient for v1 without that added complexity.
- Treating iNaturalist's higher-level ancestry (kingdom through class) as stable for this project. Reasoning: reclassifications above family are assumed rare, and iNat would be expected to notify the community of changes that high in the tree — not independently verified, taken as a working assumption.
- Rename the (county_id, taxon_id) dataframe from a "species" name to "observations" — decided in principle, since rows represent one observation-count pairing per county/taxon, not one row per unique species.
- Column naming convention for taxa: use a clear, common one-word English name for a high-level taxon group where one exists (e.g. "plant", "animal"); fall back to the scientific/taxonomic name only where no clear common one-word equivalent exists. Reasoning: scientific names were considered throughout for consistency but judged to cost some code readability compared to plain English where a clear common term is available.

## Tried/Built

- Confirmed via a Plotly community forum example that `updatemenus` dropdown/buttons can restyle color/`z` values within a single exported static HTML file. This resolved the open hosting question from a prior session: static export (e.g. GitHub Pages) is sufficient since Phase 1 requires no Python retouch at request time — all six group dataframes are precomputed.
- Identified that Plotly's `restyle` does not auto-recalculate the color range when `z` is swapped — the range must be explicitly passed in each button's `args`, requiring precalculated min/max per group. Not yet implemented.
- **Dead end:** previously attempted a log-transformed color scale to compress large values. Abandoned — hover numbers and the legend stopped being meaningful relative to the raw data. Parked as a possible future refinement (likely fix identified in discussion: color by log-transformed value while keeping raw value in `customdata` for hover — not attempted yet).
- Built and saved the taxon-level dataframe (fill + save step complete).
- Worked through confusion between `np.where` (elementwise value-or-value substitution, same length in/out), `DataFrame.where` (keeps value where condition True, replaces with `other` where False), and `.assign()` (attaches a column; does not itself compute values). Resolved through discussion.
- Wrote a first-draft classification expression:
  `df_county_species_taxonomy_df.assign(is_plant=lambda x: np.where(x['ancestry'].str.startswith(PLANTS_ANCESTRY_PATH), x['all_species_count'], np.nan))`
  Flagged issues, not yet resolved (see Open). Naming resolved after the fact: the row-level column will be `plant_count` (not `is_plant`); once aggregated at the county level via `.agg()`, the resulting column will be `flora_species_count`.
- Confirmed the ancestry path constant is stored with a trailing slash (e.g. `"48460/1/2/355675/"`) specifically to prevent `startswith` false-positive matches against similar-prefix taxon IDs.
- Generated and reviewed two Phase 1 choropleth outputs: vertebrate species count by county, and arthropod species count by county (saved as `vertebrate_species_count_by_county.png` and `arthropod_species_count_by_county.png`). Observed Boulder County ranks much higher on arthropod count relative to its vertebrate ranking — read as likely observer-effort/expertise bias (arthropods are harder to notice and identify) rather than a true biodiversity signal, consistent with the previously named observer-bias limitation.

## Open

- Whether `x['all_species_count']` (used as the true-value in the flora/fauna/vertebrate `np.where` calls) is a clean per-row observation count, or already carries NaN in some rows from the earlier native/invasive filtering logic — not confirmed. If the latter, flora/fauna/vertebrate counts could be silently wrong for taxa that happen to be NaN in `all_species_count` for unrelated reasons.
- The `.assign()` call producing the plant classification column is not yet caught/reassigned to a variable — as written, it currently has no effect on the dataframe.
- Final column names for the fauna and vertebrate equivalents (row-level and aggregated) not yet finalized — apply the same naming convention decided above (plain-English one-word name where clear, scientific name otherwise) once the counterparts to `plant_count`/`flora_species_count` are written.
- Renaming the county/taxon dataframe and related variables from "species" to "observations" terminology — decided in principle, not yet done in code.
- Precalculating min/max color ranges per group dataframe, to be passed alongside `z` in each dropdown button's `args` — not yet built.
- Colorado-specific gap in ancestry-based vertebrate classification (vertebrate classes with no dedicated `iconic_taxon_name`) — judged likely rare/low-impact for CO's landlocked fauna, not verified empty.
- Whether to keep ancestry-path matching long-term for Vertebrates or fall back to a simpler `iconic_taxon_name` union if the CO-specific gap proves trivial — left open by design; both fields are stored to preserve the choice.
- **Risk flagged during fact-check, not yet tested:** the dropdown/button `restyle` approach was validated against a Plotly community example using the older `choropleth` trace type. This project uses `choropleth_map` (the newer MapLibre-based trace, per the ArcGIS/`featureidkey` work in prior sessions). A Plotly.js GitHub issue reports that `restyle` and `update` do not reliably swap `z`-data or colorscale on `choroplethmapbox`/`choroplethmap` traces — only `relayout` was confirmed working there. Not yet spot-checked against this project's actual trace type; needs a direct test before more time is invested in the button-based group/dataset switcher.

## Next

1. Spot-check whether `restyle` actually updates `z`/color on a `choropleth_map` trace specifically (minimal test: one trace, one button, confirm the map visibly changes) before building the real six-group dropdown on top of that assumption.
2. Fix the plant classification assignment: catch the `.assign()` return value, apply the `plant_count` naming, and verify whether `all_species_count` is already NaN for unrelated reasons before trusting the flora/fauna/vertebrate counts built on top of it.

**Named but not yet scoped, in stated order of intent:** dropdown UI polish/styling; precalculated color ranges per group; site setup for public exploration (GitHub Pages, per the hosting decision above); write-up for GitHub; posts for iNaturalist forums and Discord; show-and-tell presentation for the college friend group; personal-website write-up (longer-term, unscoped).