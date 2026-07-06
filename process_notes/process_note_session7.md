# Session — 2026-06-29

**Time:** ~6:50 PM to 8:19 PM
**Focus:** DataFrame serialization (Parquet), caching design groundwork, timestamp/metadata reasoning

## Decided

- Chose **Parquet** over Feather for saving dataframes to disk. Reasoning: confirmed directly in the pandas docs (`to_feather` requires a default index — no custom index support; `to_parquet` does). No custom index exists yet, but Parquet was chosen preemptively "just in case" one gets added later, avoiding a forced format-switch down the line.
- Learned via search: you don't need to write code against the PyArrow API directly — but it (or fastparquet, as an alternative) is a required dependency for `.to_parquet()`, not just incidental machinery; pandas needs one of the two installed to write Parquet at all. `.to_feather()` is built specifically on the Arrow/Feather format, so PyArrow is effectively required there too, with no fastparquet-style alternative.
- Discussed (and have now separately verified) that there's no hard pandas limit on dataframe width — practical limit is just RAM and performance, far from relevant at 64 counties. Noted (not acted on): a wide dataframe is often a sign that something which should be rows got turned into columns instead — worth keeping in mind as more metrics get added, not a current problem.
- Decided to keep dating data via the **filename** for now (not a per-row column), judged "good enough for the moment." Explicitly tabled a more complex idea (see below) rather than solving it tonight — correctly sized as real complexity not needed yet.
- Reflected on the standing choice to build this as structured/organized code rather than Jupyter notebooks. Reasoning, named directly: notebooks would have allowed faster visible iteration in the moment, but also would have let old, half-working cells sit unattended and out of order. Working in proper code files forced cleanup that the faster tool would have let slide — a deliberate trade of immediate-feedback speed for an actually-maintainable, understandable codebase.

## What was tried / built

- Parquet save/load working and confirmed functional.
- Worked through (but explicitly tabled) the timestamp/caching ambiguity problem: once caching is added, "last updated" becomes ambiguous — it could mean either (a) the underlying iNat data changed, or (b) the local code/logic changed and was rerun against the same underlying data, producing a "new" timestamp on identical source data. These are different things worth tracking separately if pursued, but recognized as more complexity than needed right now. Tabled deliberately, not avoided — the reasoning is preserved here for whenever it's picked back up.
- Originally planned to add per-metric timestamp columns (e.g. `native_species_count_date`) to solve the filename-date fragility problem from a past job (CSV files renamed/moved losing their date metadata, ambiguity between "date produced" vs "date sent"). Mid-thought, pivoted toward caching API responses by filter combination instead, recognizing it solves a related but distinct problem: timestamps answer "is this data stale," caching answers "have I already asked this exact question and can skip re-asking." Not in conflict — just different problems, both surfaced from the same train of thought.

## Reflection: process note

Named directly tonight: progress felt slow, with a want to *see or feel* technical improvement rather than just reason through design decisions. Clarified what that meant concretely — the caching/disk-save work is upstream/structural, not yet visible as a faster iteration loop. The actual payoff (being able to quickly create, tweak, and rerun new metrics like species count or density without re-hitting the API each time) is expected once caching is wired in, not yet realized tonight.

Also worth flagging as a recurring pattern across sessions, not just tonight: doing things the *harder-right-now* way repeatedly trades immediate ease for something more manageable later — not necessarily "easy" later, but more workable. Tonight's example: organized code over notebooks, slower to iterate visibly in the moment, but prevents the kind of mess that would need cleaning up after the fact. This mirrors the FIPS-field fix and the per-population dead-end from earlier sessions — paying a higher cost up front for a result that holds up better afterward.

## Open questions / not yet started

- Timestamp ambiguity (data freshness vs. code/logic freshness) — tabled, reasoning preserved above, not designed.
- Caching by filter combination — decided in principle in an earlier session (cache common combinations like Denver/plants+animals/native, skip caching rare ones), not yet implemented.
- Uncommon-species filtering — still not started, carried over from 6/27.

## Concrete next step

Continuing tonight: implement the API response caching (by filter combination) and disk-save, since this is the piece expected to actually deliver the "quickly iterate on new metrics" feeling that's currently missing. **Flag for next check-in:** ask directly once caching is built and in use whether it actually produced that faster, more visible iteration loop, or whether the felt slowness persists for a different reason.