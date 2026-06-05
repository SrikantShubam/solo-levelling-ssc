# solo-levelling-ssc

SSC CGL question corpus extracted from 19 PDFs (2019-2024, Tier 1 & 2) with an AI-powered study application for spaced repetition practice.

## Corpus Stats

- **2355 questions** across 19 PDFs
- **99.3% precision** (valid question text + options + numbering)
- **~97% recall** on extractable content
- **67% answer coverage** (higher on portal response sheets, lower on prepp papers)
- Pipeline: `gemini-3.1-flash-lite` at 60 RPM, spot-fixed with `gemini-3.5-flash` for tricky pages

## Structure

```
pipeline_output/p2_gemini/   ← winning pipeline output
  {pdf_name}/
    merged_questions_global_order.json   ← final merged questions
    page_json/                           ← per-page extraction results
    review_summary_*.md                  ← QC reports
deprecated/                  ← old pipeline attempts
src/
  ssc_study/                 ← Phase 2b: study application
    cli.py                   ← rich-click CLI (5 commands)
    models.py                ← domain dataclasses
    db.py                    ← SQLite schema (13 migrations, 10 tables)
    loader.py                ← corpus ETL with idempotent import
    sm2.py                   ← SuperMemo 2 spaced repetition
    scheduler.py             ← SM-2 review scheduler
    quiz.py                  ← interactive quiz engine
    embeddings.py            ← sentence-transformers + FAISS semantic search
    archetypes.py            ← 40+ keyword-based archetype classifiers
    cards.py                 ← GK/GA fact card extraction
    reports.py               ← session/daily practice reports
    timer.py                 ← cross-platform input timer
    config.py                ← JSON config persistence
    _normalize.py            ← section name normalization
reports/                     ← phase comparison reports
tests/                       ← 113 tests (pytest)
```

## Commands

### Corpus extraction

```bash
ssc-corpus extract-pdf --pdf <path> --out <dir> --provider gemini --model models/gemini-3.1-flash-lite
```

Run with `--help` for full options. Requires a `.env` file with `api=<gemini-key>`.

### Study app

```bash
# Import the corpus into SQLite
ssc-study import

# Verify import integrity
ssc-study verify

# Start a practice quiz
ssc-study quiz --session-type mock --count 25

# SM-2 spaced repetition review
ssc-study quiz --session-type sm2_review --count 20

# Show practice reports
ssc-study report --daily
ssc-study report --session 1

# View/edit configuration
ssc-study config --show
```

## Study app features

| Feature | Description |
|---------|-------------|
| **SM-2 spaced repetition** | Canonical SuperMemo 2 algorithm with all 6 documented pitfalls covered |
| **Interactive quiz** | Timed questions with skip/timeout, scored responses, SM-2 state persistence |
| **Review scheduling** | Due-for-review queries prioritizing overdue cards, then new material |
| **Semantic search** | Sentence-transformers + FAISS for similar-question remediation |
| **Archetype classification** | 40+ keyword-based archetypes across all 5 SSC sections |
| **Fact card generation** | GK/GA factual knowledge extraction into front/back memory cards |
| **Cross-platform timer** | msvcrt (Windows), select (Unix), threading fallback |
| **Configuration** | JSON-persisted user settings with sensible defaults |

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ Pipeline    │────▶│ SQLite (WAL) │────▶│ Study App    │
│ (19 PDFs)   │     │ 10 tables    │     │ (ssc-study)  │
└─────────────┘     │ 13 migrations│     └──────────────┘
                    │ 2355 q + emb │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ SM-2 State   │
                    │ per question │
                    └──────────────┘
```

## Phases

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ | PDF acquisition + integrity |
| Phase 2 | ✅ | Corpus extraction (all 2355 q) |
| **Phase 2b** | **✅** | **SQLite, study app, SM-2, embeddings, archetypes, fact cards** |
| Phase 3 | 🔜 | Atlas — adaptive difficulty engine |
| Phase 4 | 🔜 | Guardian — full mock test simulator |

## Development

```bash
pip install -e ".[dev,study]"
python -m pytest tests/ -v
ruff check src/ssc_study/ tests/
```
