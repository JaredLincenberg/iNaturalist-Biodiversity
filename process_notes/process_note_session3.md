# Session — 2026-06-24

**Time:** 10:30, ended 11:33 PM
**Focus:** County boundary resolution for CO choropleth map

## Decided

- Confirmed the original GeoJSON (pulled via `json.load()` from a GitHub-hosted example) was too low-resolution for county shapes — blocky/jagged boundaries, not a code bug.
- Reasoning: that file is a common "good enough for a glance at the whole US" demo dataset, not built for zoomed-in single-state detail. Low res is an inherent property of the source, not something to debug around.
- Chose to switch sources rather than try to fix/smooth the existing file.

## What was tried / built

- Found Colorado's GIS spatial data portal (`geodata.colorado.gov/pages/spatial-data-portal#Boundaries`).
- Initially landed on an ArcGIS Hub "explore" page for a dataset called "USA Census Counties." Confirmed via fetch: sourced from 2023 Census TIGER/Line data, includes county boundaries for all 50 states + DC, with population estimates. Legitimate high-res source — but hosted via ArcGIS Hub, not a plain repo, so no direct raw-JSON URL like the old GitHub example had.
- **Dead end avoided:** almost treated the ArcGIS "explore" page as if it would give a simple downloadable JSON link the same way the GitHub example did. It doesn't — ArcGIS Hub serves data through a feature service API instead.
- Found the actual access path: the ArcGIS REST "Query Feature Service Layer" endpoint, documented at `developers.arcgis.com/rest/services-reference/enterprise/query-feature-service-layer/`.
- Pulled the GeoJSON from that endpoint and inspected its `properties` — found the FIPS-equivalent field had a different name than Plotly's example data used (`"fips"` in the tutorial vs. ArcGIS's own field name).
- **Root cause identified:** Plotly's `choropleth_map` needs `featureidkey` to be told explicitly which property in the GeoJSON to match against the location values in the dataframe. The mismatch wasn't a bug — it was two systems using different field names for the same FIPS identifier.
- Fixed by setting `featureidkey` to point at the correct property path in the new GeoJSON.
- Got the map rendering successfully using Plotly's example **unemployment** dataset as a stand-in, with the higher-resolution Colorado county boundaries.

## Open questions / next time

- None outstanding on the boundary-file front — that problem is solved.
- Not yet started: building the actual dataframe from the personal species-count CSV.
- Not yet decided: what color scale/colormap to use for species count (vs. the unemployment example's default).

## Concrete next step

Replace the unemployment example dataframe with a dataframe built from the species-count CSV, and point the choropleth's color argument at the species-count column instead of unemployment rate.