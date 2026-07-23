# Process Note — 2026-07-22 (afternoon/evening session)

**Session time:** 4:23 PM–9:19 PM.

## Decided

- **README audience: developers/employers evaluating the code.** Distinct from the site article's audience (casual Colorado outdoor enthusiasts). Initial framing attempt ("what should an employer walk away feeling") was corrected — a README is primarily what-it-is / how-to-install / how-to-run, with additional context as optional depth after that core.
- **Cache vs. deliverable is about behavior, not file format.** The dividing line is whether the code refetches/rebuilds a file from the API if it's missing, not `.parquet` vs `.csv`. Established by tracing every file path in `main.py`.
- **`cache/` fully gitignored; no pre-warmed cache distribution.** Distributing a warmed cache (so others skip ~500 requests) was raised but parked — it's a GitHub Release-attachment mechanism, not a `.gitignore` line. Default chosen: fresh clones pay the request cost.
- **`expire_after` set to one week.** Tradeoff named: shorter means fresher counts but more repeated requests during development; longer means fewer requests but staler numbers.
- **`inat_{stateName}_counties.csv` stays CSV in `data/processed`, not parquet.** Reasoning: an end user can open it to check the county list. Prefix added to clarify the file's source/purpose.
- **State-generic scope limited to single state.** Multi-state/regional support (e.g. "New England counties") and robustness to iNaturalist name changes were named as the full version of the problem and explicitly parked. Reasoning: `get_iNat_county_data()` predates the project's current discipline and is more tangled, so generalizing it is not a parameter tweak.
- **State identification via iNat place ID only, no crosswalk table.** Two ID systems are in play (iNaturalist internal place IDs vs. Census/FIPS identifiers used by the ArcGIS layer). Rather than maintain a translation table, the state's `Name` is read from the row already being looked up in `places.csv` and matched against ArcGIS's `STATE_NAME` field. End user only sets the state ID.
- **README gets a Process section, not an "AI usage" disclosure section.** Reasoning: framing as a deliberate working method (linking `process_notes/`) rather than a disclosure avoids reading as defensive, while conveying the same information. Personal/motivational detail deliberately excluded and reserved for a future `process.md` or site page.
- **"All code here is written by me" cut as a standalone claim**, replaced with a more accurate statement about snippets/autocomplete/tutorials being included only where verifiable and implementable. Reasoning: the blanket claim is less credible to a skeptical reader than the qualified one.
- **DMO success criteria excluded from the README intro.** Considered and rejected — keeps the intro about the project rather than the process, which the Process section already covers.

## Tried / built

- Full file inventory traced from `main.py`, producing four categories: required static input (`data/raw/inaturalist-places.csv`, 187k rows, read-only, never written by code); self-healing caches (dated parquet files, the `requests_cache` SQLite db, and `colorado_counties.csv` — which behaves as a cache despite its format); deliverable output (`colorado_county_species_count_<date>.csv`); final render (`docs/index.html`).
- Confirmed via `requests_cache` docs that its SQLite backend creates parent directories automatically — `cache/` needs no manual pre-creation, and no setup step in the README.
- Confirmed no API key/config is required (all endpoints public), that the script must run from repo root (all paths relative to root), and that `requirements.txt` is a clean `pip freeze`.
- Made `get_iNat_county_data()` state-generic (single state), with a working `force_refresh`, writing `inat_{stateName}_counties.csv`. Reported as producing correct output for Colorado.
- `get_county_geometry()` identified as also hardcoding Colorado (`STATE_ABBR='CO'`). Parked pending the data-source decision, which was subsequently resolved (match on `STATE_NAME` using the name already available from `places.csv`). Two side issues flagged, not fixed: it stores the raw `requests.Response` rather than parsed GeoJSON, and unlike `get_County_Species_Counts` it has no try/except around the request.
- ArcGIS layer documentation located and field list confirmed directly from layer metadata (`USA_Census_Counties/FeatureServer/0`): `OBJECTID`, `NAME`, `STATE_NAME`, `STATE_ABBR`, `STATE_FIPS`, `COUNTY_FIPS`, `FIPS`, `POPULATION`, `POP_SQMI`, `SQMI`, plus shape fields. Source is 2020 Census TIGER via Esri, updated annually; last data edit 11/21/2024.
- `.gitignore` updated for `cache/`; writes reported as landing in `cache/` rather than `data/processed`.
- Empty-`cache/`-directory question raised: Git does not track empty directories at all, so a `.gitkeep` placeholder is required. Flagged that a bare `cache/` ignore pattern would also ignore the placeholder — needs `cache/*` plus `!cache/.gitkeep`. Not confirmed as applied this session.
- README draft built section by section: title, live site link, Introduction, Installation (Python 3.14, venv, pip install), Running (repo-root requirement, first-run cost, cache behavior, `docs/index.html` overwrite), Process (session structure, `process_notes/` contents, LLM use).
- Process and Introduction sections revised across multiple passes. Process section restructured from prose to a hybrid — bulleted lists where content is genuinely a list, prose for the LLM-use paragraph, on the grounds that its "started as X, became Y" movement doesn't survive fragmentation.

## Open

- `.gitkeep` + `cache/*` / `!cache/.gitkeep` pattern not confirmed applied.
- Python version stated as "developed on Python 3.14" rather than a tested minimum floor — the actual lower bound is untested.
- CSV download feature for `colorado_county_species_count_<date>.csv`: confirmed not to exist anywhere in the templates or code. Intended but not built.
- `get_county_geometry()` still hardcodes `STATE_ABBR='CO'`; also stores raw response rather than parsed GeoJSON, and lacks error handling.
- `data/processed` still accumulates a dated CSV per run; gitignore treatment undecided (a `data/sample` folder was floated). Noted that "viewable to the end user" could mean browsable in the repo or downloadable from the site — different gitignore answers.
- Logging: replacing narration `print()` statements with the stdlib `logging` module (level-toggleable, nothing to install) was raised and deferred without decision.
- Multi-state/regional county filtering (1.1).
- GitHub Action to watch/redownload `inaturalist-places.csv` when updated (1.1).
- Staggered/chunked cache refresh (1.1).
- Dated parquet re-deriving daily from source data that rarely changes — flagged as possibly redundant, not investigated.
- README sections not yet written: usage/configuration (`force_refresh`, state parameter), data sources, limitations.

## Next

Apply the `cache/*` + `!cache/.gitkeep` gitignore pattern and confirm `cache/` persists as an empty directory on a fresh clone, then reinstall the project in a new directory as a clean-install test — including checking whether Claude Code can interact with it correctly.

## Separate

Ideas raised during sessions that aren't build work on this project:

- Compare the project's Socratic-method instructions against actual writings on the Socratic method, or against teaching material on it.

## Process/tooling notes

- Repo pulled fresh via `codeload.github.com` tarball at session start rather than the GitHub contents API, avoiding the rate limit hit in session 18.