# Process Note — 2026-07-14

**Session time:** 8:06 PM – 9:16 PM (1h10m)

## Decided

- **V1.0 scope defined as a tagged task list** (CODE / STRUCTURE / WRITING), derived from diffing the current `main.py` against the five self-authored "definition of done" criteria plus parked threads. List lives in `v1_todo.md`. Reasoning: needed a bounded, checkable target so "done" measures against the five criteria, not against totality.
- **Rare-species threshold implemented as two toggleable buttons (>2, >5), not a single baked-in filter.** Reasoning: makes the threshold a user-facing view the reader can switch between, consistent with the existing metric-switcher pattern (swap `z`), rather than one hidden pre-agg mask.
- **Threshold applies only to `all_species_count` in V1.0** — no other metric gets min-count filtering. Reasoning: scope discipline; filtering already-small counts (e.g. invasives) risks emptying the map, and the combinatorial column expansion (metrics × thresholds) isn't worth it for V1.0.

## Tried / built

- **C1 done.** Threshold columns built via named aggregation on the long-format `(county_id, taxon_id, all_species_count)` frame, before the county rollup:
  - `all_species_count_min2=('all_species_count', lambda s: (s > 2).sum())`, `_min5` likewise.
  - Key insight landed by Jared: `(s > N)` returns booleans; `.sum()` counts the Trues, so it counts *qualifying taxa*, not observations — no NaN round-trip needed.
- **Reconsidered: NaN-then-count approach.** Initial idea was a function returning NaN for sub-threshold rows then `count`. Reconsidered after distinguishing summing observations from summing booleans — once it was clear `(s > N)` yields booleans that `.sum()` counts directly, the NaN round-trip was unnecessary.
- **Rejected: pre-masking the frame twice** (`df[df['all_species_count'] > n]` run per threshold). Chose the in-agg lambda instead for the one-pass, all-columns-together form.
- **`{'col': 'func'}` dict form couldn't create new output names** (key collision on `all_species_count`). Switched to named aggregation via `**`-unpacked dict of `output_name: (input_col, func)`. Side benefit: absorbed the old post-agg `.rename()`, removing that step entirely and making the agg clearer.
- **Spot-check passed:** `min5 < min2 < all` ordering holds across several counties checked (not exhaustively verified) — confirms the mask direction/threshold aren't crossed.

## Open

- **Write-up divergence flagged, not yet resolved.** Pair 3 raw text says the `>5` filter "was applied" as a one-time step; code now offers `>2`/`>5` as switchable views. W1 must reword to match. Logged in the C1 entry of `v1_todo.md`.
- **`v1_todo.md` could not be uploaded to the Drive project folder** — `create_file` errored three times despite the folder being confirmed writable. File is maintained locally and re-presented after each change. Known interface unreliability; workaround pending.

## Next

Pick the next V1.0 item from `v1_todo.md`. C1 is the only completed task. Candidate next: commit the C1 agg change (self-contained unit) before starting anything new, per the regular-checkpoint commit habit.