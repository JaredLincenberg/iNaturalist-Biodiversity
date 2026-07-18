# Process Note — 2026-07-15 (afternoon/evening session)

**Session time:** Two blocks this day: C2/C4 in the 4:27–4:58 PM window (confirmed done at 6:00 PM); C3 onward 6:01–7:56 PM.

## Decided

- **C2 parked to 1.1, not fixed.** The dead `get_species_density` function divides species count by area/population — realized this is a *metric*, not a bias fix. Area/population does not correct observer bias (Boulder is bright from dedicated observers per capita, not people or land). Moved to `src/parked/`; deliberately showing null/deferred work rather than silent deletion (DMO #3). Split into two 1.1 items: (a) area/population density as a show-and-tell metric a friend asked for, (b) true observer-effort normalization as the real bias fix.
- **C4 deleted, not parked.** `add_..._old` is a *superseded* version, not a deferred feature → git history is the right home. Rationale became a standing learning: side effects + temporal coupling + retry-on-failure + data dependencies make it hard to revive; contrast the pure/local C1 agg lambda.
- **C3: invasive → introduced.** Confirmed via iNaturalist search-URLs page: `native=false` returns unknown OR introduced; `introduced=true` returns only introduced. Switched the invasive query to `introduced=true` — fixes the wrong-bucket problem and dissolves the original key collision. Naming fact: API filters `introduced` (establishment means), not "invasive" (a stronger ecological claim). W1 impact tracked in Open.

## Tried / built

- **C6 done:** requirements.txt generated and double-checked.
- **Verified native/introduced/unknown meanings (no code change):** the four-state establishment-means model — native=true (native/endemic), introduced=true (introduced), and the two false-queries each leaking "unknown." Neither flag's false equals the other's true. Confusion arose from inspecting `introduced=false` results (= unknown + native + endemic), not a bug.
- **C5 reframed, still open:** started as button-1/default-metric check; became "color schemes in general." `get_map_buttons()` is the metric-button function (briefly mistaken for a Plotly built-in); colorscale has its own separate button function and owns its state. Metric buttons deliberately don't set initial colorscale.

## Open

- **C5** — color schemes in general: initial colorscale state + behavior across metrics. Needs its own scope next session.
- **C7 (new)** — add an "unknown" establishment-means count (native=false AND introduced=false): taxa with no establishment means recorded for the place. Currently invisible inside both false-queries. Surfacing it supports write-up honesty (DMO #3/#4).
- **Write-up (W1) impact:** Pair 3 talks about "invasive"; data actually measures "introduced." Must reword at W1.

## Next

Pick up C5 with a fresh scope: define what the initial colorscale should be and how colorscale should (or shouldn't) change when the metric changes. Alternatively, C7 (add the unknown count) is a small, self-contained coding task if a quick win is wanted first.

## Process/tooling notes
- `v1_todo.md` still can't upload to Drive (create_file errors); maintained locally, re-presented after each edit.
- Citation failure this session: a claim was stated as "explicit" in the docs and referenced the v2 API page, when the actual source was the community search-URLs page. Correct going forward: name the exact page and quote the exact line for any claim to be acted on.