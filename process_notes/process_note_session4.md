# Session — 2026-06-26

**Time:** ~7:11 PM to 9:45 PM
**Focus:** Normalizing species counts (area, population), code cleanup/caching

## Decided

- Parked two ideas raised mid-session to avoid scope creep: (1) expanding to all US counties (blocked on finding iNat's state ID scheme, same problem solved for counties), (2) restricting species to "easily observable" plants/animals only. Both are real but separate from today's task — noted for later, not pursued now.
- Chose to add **area-normalization first** (species per sq mi), with population-normalization and observer-count-normalization parked as the next candidates to try, not built today.
- Reasoning for area over the others initially: quickest to implement, lets the matching/plotting pipeline get exercised end-to-end before adding more complexity.
- Mid-session, surfaced a sharper question than originally posed: dividing by area answers "how big is this place," not "how thoroughly was it searched" — which is closer to what's actually wanted for a fair biodiversity comparison. Observer-count or population as denominators were named as more direct fits for that question. Not built yet, but the reasoning is now explicit for next time.
- Distinguished "refactor" from "clean up" as different-risk activities (refactor changes behavior risk profile, cleanup doesn't) — settled on doing light cleanup (stray prints, unused code) folded into the same pass as the area-division work, accepting the tangling risk rather than doing a separate pass.

## What was tried / built

- **Area normalization (species per sq mi):** built and working. Results: Broomfield and Denver highlighted as high; Boulder and Gilpin also above average.
- **Population normalization (species per population):** built and working, but diagnosed as essentially an inverted population-density map in disguise — not a useful biodiversity signal. Root cause identified: species counts cluster in a narrow range while population spans many orders of magnitude, so the population term dominates the ratio regardless of actual species richness. Result mainly highlighted very low-population counties (San Juan, Hinsdale, Mineral, Jackson) — an artifact of small denominators, not a biodiversity finding.
- **Log-of-population experiment:** tried taking the log of the population denominator to see if it revealed anything new in high-population counties, based on a prior (unsaved) experiment where log on density had expanded color contrast. Result: expanded the color spread as expected, but confirmed it does not surface new signal — same low-population counties just more visually prominent. Logged as "maybe useful later" rather than a finding. Correctly identified as a visual-contrast change, not a conceptual fix — log doesn't address the underlying area/population mismatch in what's being measured.
- **Refactor — extract method + singleton/global for API data:** restructured so the iNaturalist API is called once and cached, readable from multiple places without re-fetching. Confirmed: most of this is read-only after first fetch. Exception flagged: the county-level DataFrame, where new columns get added after the fact — this still mutates shared state and needs rethinking (not solved today, flagged for later).
- **Observed effect of the refactor:** extracting the method made it noticeably faster to tinker with new metrics — directly enabled trying area, population, and the log variant in one session instead of redoing setup each time.

## Open questions / next time

- DataFrame mutation (adding columns to the cached county-level data) still needs a real solution — flagged, not designed yet.
- Which normalizer actually answers "most biodiverse" fairly — area, population, and observer-count have different flaws/fits; observer-count not yet tried.
- US-counties expansion blocked on finding iNaturalist's state ID equivalent to the county ID lookup already solved.
- Plants/animals-only species filter not yet started.

## Concrete next steps (named for next session)

1. Add a selector/toggle to switch between the different metric maps (area, population, etc.) without re-running everything manually.
2. Explore whether the different metric maps can be overlaid in one view.
3. Grab screenshots of the test maps under the different metrics — needed for the write-up, even just as basic supporting images.