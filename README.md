# Zepto Data & AI Platform — Capstone

Certificate Program in Artificial Intelligence and Machine Learning — capstone project.

## Overview

This repository contains three independent, self-contained modules that together
demonstrate a data-to-AI platform workflow: a web scraping and SQL data pipeline, an
exploratory-analytics and machine-learning study, and a retrieval-augmented support
assistant. The three modules do not import from one another; each is graded and run
independently.

| Module | Folder | Marks | What it does |
| --- | --- | --- | --- |
| 1. Data Pipeline | [`data_pipeline/`](data_pipeline/) | 25 | Scrapes books.toscrape.com, cleans and normalizes the data, loads it into SQLite, and validates SQL query output against pandas. |
| 2. Analytics + ML | [`analytics/`](analytics/) | 50 | Full EDA and machine learning study on the Titanic dataset: profiling, visualization, classification, imbalance handling, hyperparameter tuning, and regression. |
| 3. Support Assistant | [`support_assistant/`](support_assistant/) | 25 | A retrieval-augmented Q&A API over a small policy-document corpus, built with LangGraph and served with FastAPI. |

## Requirements strategy

Two `requirements.txt` files, by design:

- **Root `requirements.txt`** — consolidated, covers all three modules' dependencies
  (scraping, data science, ML, embeddings, LangGraph, FastAPI). Used for local
  development across the whole repository.
- **`support_assistant/requirements.txt`** — a slim subset, used only by the
  `support_assistant` Dockerfile, so the container image doesn't carry dependencies
  (scraping, Jupyter, matplotlib, etc.) it never needs.

## Setup

```bash
git clone <this-repo-url>
cd zepto-data-ai-platform-capstone
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
```

`sentence-transformers` pulls in PyTorch (~2GB) — the install takes a few minutes.

## How to run each module

### Module 1: Data Pipeline

```bash
python -m data_pipeline.run_pipeline        # scrape -> clean -> load (needs internet)
pytest data_pipeline/tests -q               # offline parser tests
python -m data_pipeline.queries             # run and print all 5 SQL queries
python -m data_pipeline.pandas_validation   # prove SQL JOIN == pandas merge
```

Real result from the committed `books.db`: 474 books across 9 categories (target was
>=60 books / >=3 categories). Full write-up: [`data_pipeline/README.md`](data_pipeline/README.md).

### Module 2: Analytics + ML

Open `analytics/01_eda.ipynb` then `analytics/02_modeling.ipynb` in Jupyter/VS Code
and run all cells in order, or:

```bash
python analytics/reload_test.py             # proves the saved pipeline predicts on raw input
```

Real result: the tuned Random Forest + SMOTE pipeline achieves test F1 = 0.7518;
regression on `fare` achieves Adjusted R2 = 0.3617. Full write-up:
[`analytics/README.md`](analytics/README.md).

### Module 3: Support Assistant

```bash
python -m support_assistant.ingest          # build the ChromaDB collection
pytest support_assistant/tests -q           # offline tests, no network needed
uvicorn support_assistant.main:app --port 8000
```

Docker (requires Docker Desktop):

```bash
docker build -t zepto-support ./support_assistant
docker run -p 7860:7860 zepto-support
```

Both real build and run were verified end-to-end (see
[`support_assistant/README.md`](support_assistant/README.md) for real logs and JSON
responses). Runs with `MOCK_LLM` unset by default — zero network calls, no API key,
no LLM SDK required.

## Design decisions per module

**Module 1:** category-listing pages scraped (not "All products") so `category` is
available without an extra request per book. `GBP_TO_INR = 105.50` is a fixed
project-defined constant, never a live FX call. Rows that fail to parse are dropped
rather than imputed (see [`data_pipeline/README.md`](data_pipeline/README.md) for
the full justification).

**Module 2:** `sns.load_dataset('titanic')` called exactly once in the whole module.
`alive` is dropped before any modeling — it is `survived` recoded as text, perfect
target leakage. Stratified train/test split before any preprocessing; all
imputation/encoding/scaling fit only on the training split via `ColumnTransformer`
inside a `Pipeline`. SMOTE applied to the training fold only, via
`imblearn.pipeline.Pipeline`. The persisted artifact
(`analytics/models/best_pipeline.joblib`) is the full pipeline, not a bare estimator.

**Module 3:** `MOCK_LLM` is read in exactly one place (`support_assistant/config.py`)
and defaults to mock mode — the graded path. No LLM SDK is imported at module scope
anywhere; the optional real-LLM path lives entirely in `support_assistant/llm.py`,
imported only inside function bodies. Routing (`classify_intent`) never depends on
`MOCK_LLM` — only answer generation does.

## Git workflow

Three feature branches, each with multiple commits, each merged into `main` via a
real GitHub Pull Request merge commit (not squashed, not fast-forwarded):

- `data-pipeline` -> `main` (Module 1, 7 commits)
- `analytics` -> `main` (Module 2, multiple commits across EDA and modeling)
- `support-assistant` -> `main` (Module 3, multiple commits)

Verify with:

```bash
git log --graph --all --oneline --decorate
```

## Testing

| Module | Command | What it proves |
| --- | --- | --- |
| 1 | `pytest data_pipeline/tests -q` | Parser handles price/rating/availability offline, using a saved HTML fixture |
| 1 | `python -m data_pipeline.run_pipeline` | >=60 rows, >=3 categories, correct dtypes, FK integrity, INR math |
| 2 | Notebook assertion cells | Correlation matrix shape (6,6), stratified split, no test-set fitting |
| 2 | `python analytics/reload_test.py` | Joblib artifact predicts from raw, unprocessed input |
| 3 | `pytest support_assistant/tests -q` | Both routing branches, retrieval correctness, canned strings, confidence bounds, no network in mock mode |
| 3 | `docker build` + `docker run` + real `/ask` calls | Image builds and serves requests with no API key, no runtime network |

## Troubleshooting log (real issues hit during this build)

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Â£51.77` in scraped price | Response encoding not set before reading `.text` | `response.encoding = "utf-8"` before `.text` |
| `pytest` `ModuleNotFoundError` for a local package | `tests/` folder lacked `__init__.py`, so pytest's rootdir-walk stopped early and never added the repo root to `sys.path` | Added `__init__.py` to both the package and its `tests/` folder |
| PyTorch install failed with `WinError 206` (path too long) | Project sits inside a long OneDrive path; PyTorch ships deeply-nested license files | Enabled Windows long-path support (`LongPathsEnabled` registry key) |
| `\ufeff` (BOM) character appearing inside retrieved/answered text | PowerShell's `Out-File -Encoding utf8` writes a UTF-8 BOM; `ingest.py` read files with plain `"utf-8"` | Changed to `encoding="utf-8-sig"`, which strips a leading BOM if present |
| `curl.exe` calls with escaped quotes failed (`Could not resolve host: is`, etc.) | PowerShell's string quoting mangled backslash-escaped JSON before curl ever saw it | Used PowerShell-native `Invoke-WebRequest` with `ConvertTo-Json` instead of hand-escaped curl strings |
| `docker` command not recognized after installing Docker Desktop | Docker Desktop installed to a per-user path (`%LOCALAPPDATA%\Programs\DockerDesktop`), not the usual `Program Files` location the terminal's cached PATH expected | Located the real install path and added it to the user PATH environment variable |
| SQL-vs-Python rounding mismatch flagged by an audit query (5 of 474 rows) | SQLite's `ROUND()` (rounds half away from zero) and Python's `round()` (rounds half to even) disagree at exact `.xx5` ties | Verified all 5 flagged rows independently against Python's `round()` (the function `cleaning.py` actually uses) — all 5 matched exactly; not a real defect |

## Optional / ungraded extensions — status

| Extension | Status |
| --- | --- |
| Live FX API for GBP->INR | Not attempted (by design — the fixed `105.50` constant is what's graded) |
| Real LLM via Groq (`MOCK_LLM=0`) | `support_assistant/llm.py` is implemented with the required retry-on-validation-failure logic, but never actually invoked against a real API (no key configured) — the graded `MOCK_LLM=1` default path is what's fully tested and verified |
| Hugging Face Spaces deployment | Not attempted — local Docker build/run (verified above) is the graded baseline |

## Submission

Single public GitHub repository, three module folders at root, no screenshots/PDFs/
slides anywhere — every result is real, reproducible command output committed as
text or Markdown.
