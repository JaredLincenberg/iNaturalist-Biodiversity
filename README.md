# iNaturalist Biodiversity Map

**Live site:** https://jaredlincenberg.github.io/iNaturalist-Biodiversity/

## Introduction

This started as a question — what is the most biodiverse location in Colorado? — and the first working map came together quickly. What followed was the longer process of interrogating that answer, leading to new questions and fixes to capture the reality of the data. The project grew into a complete portfolio piece out of wanting to share what the investigation turned up, not just the first answer.

What I created is an interactive choropleth map of species diversity across Colorado's 64 counties, built from iNaturalist data. It's both a working answer to the original question and a demonstration of an end-to-end data pipeline: pulling and caching data from a public API, processing and merging it with county-level geographic boundaries, and rendering the result as an interactive, deployed web map.

## Installation

Developed on Python 3.14. No API key or account setup required — the iNaturalist and Census/ArcGIS endpoints this project uses are all public.

1. Clone the repository.
2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running

Run from the repository root, not from inside `src/` — file paths in the code are relative to root:

```
python src/main.py
```

On a first run:
- A `cache/` folder is created automatically (SQLite-backed request cache) — nothing to set up beforehand.
- Expect roughly 500 requests to the iNaturalist API on a cold cache, so the first run takes noticeably longer than later ones.
- Cached responses are reused for a week before refreshing.

The script overwrites `docs/index.html` directly — this is the same file GitHub Pages serves, so running it and updating the live site are the same action, plus a commit and push.

## Process

Built in discrete, timed working sessions, each scoped to a limited, named task rather than open-ended work:

- Set up the counties DataFrame
- Fix the hover text that appears over a county
- Get the map height to respond to the browser window

Each session produced a process note in `process_notes/`, recording:

- What was decided, and why
- What was tried — including dead ends and the reason they were rejected
- Threads left open
- A specific next step

These are working notes, not write-ups.

**On LLM use:** Sessions used an LLM as a reasoning, scoping and debugging partner, working through an emulation of the Socratic method — questions that narrow toward a conclusion rather than delivered solutions. The intention started out as being able to write and explain every line; where code came from snippets (provided by the LLM), autocomplete, or tutorials, I included it only where I could verify and implement it myself. Over time the focus became planning and breaking work down into tasks, finding that the value was less in the writing of the code than in synthesizing the idea clearly so the code could express my intentions.