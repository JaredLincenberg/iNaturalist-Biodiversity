# Session — 2026-06-27 (Part 1)

**Time:** ~11:53 AM onward (continuing into afternoon)
**Focus:** Query parameter handling, caching/rate-limit strategy, native species counts
**Status:** Paused mid-feature, not a natural stopping point — picking back up later today or next session.

## Decided

- Chose URL/query filtering over building the toggle UI today — reasoning: filtering was already confirmed last session to be "just managing the URL" (query-level, not aggregation-level), so it was the lower-risk, more contained task to start with. Toggle UI deferred as the less-familiar, higher-effort task for later.
- Confirmed `requests.get()` has a built-in `params` dict argument for query strings — no need to hand-build query strings or look for a `.prepare()`-style step for this use case (that exists for more advanced session-reuse cases, not needed here).
- Decided against splitting "build the request" out into its own separate function for now — only one caller, one request shape exists currently; flagged as a reasonable future split if/when that changes, not a problem to solve preemptively.
- Decided against using a database for caching API results (too much for current scope) and was uneasy with a flat-file-plus-metadata approach (felt clunky) — resolved by narrowing scope: don't try to cache *any* possible param combination, only the specific common combinations actually expected to be reused (e.g. Denver county, plants+animals, native-only), letting anything outside that hit the API fresh.
- Confirmed iNaturalist's actual documented rate limit: ~1 request/second, ~10k requests/day, with 429 errors on overage. Noted real-world reports of 429s even at documented "safe" rates, so retry/backoff logic is still warranted even when nominally under the limit.
- Used a 1.5 second sleep between requests as the practical rate-limiting approach — worked, no further errors.

## What was tried / built

- Hit "Max retries exceeded with url" while pulling native counts. Initial instinct was to consider scraping as an alternative data-collection method — talked through and reconsidered: this was a rate-limit symptom (consistent with the iNat API's documented and real-world-reported throttling behavior), not a sign the API/approach was insufficient. Scraping path not pursued.
- Checked V1 API and alternate datasets for filtering options, with low expectation of finding anything substantively different from V2 — deprioritized rather than dropped.
- Noted V2 species count responses return the full per-species breakdown (not just a total count) — e.g., a 1,000-species result includes 1,000 entries. Filed as potentially useful for future per-species work, not used yet.
- **Built and confirmed working:** native species counts pulled successfully with a 1.5s delay between requests.

## Open questions / not yet started

- Saving species count data so repeated requests aren't needed (the caching design above is decided in principle, not yet implemented).
- Uncommon-species filtering — named as the next thing to try, not started.
- Singleton/cache "denotation" question (how to mark in code that something is meant to behave as a singleton) — raised, not resolved; current function returns a JSON response directly rather than going through the singleton/caching pattern used elsewhere.

## Concrete next step

Implement saving of species count results (per the narrowed caching approach: common param combinations only), then attempt the uncommon-species filter. Explicitly scoped to "what's achievable with the API now" rather than expanding into UI/toggle work or other deferred ideas (US counties, overlay view, screenshots for write-up) — those remain parked from prior sessions.

## Process note

Session paused intentionally before reaching a natural stopping point — ambiguity about next steps triggered some rumination/anxiety (in vague, non-specific terms) and a felt loss of motivation. Recognized in the moment rather than pushed through; stepped away to eat/get outside instead of continuing. Real progress (rate-limit handling, native counts working) was made before the pause, even though it didn't land on a clean finish line.