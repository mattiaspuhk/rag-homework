# swedbank-rag

A small Python RAG application that summarizes company ESG / annual reports and answers a fixed set of questions using only the provided document content. Built as the Swedbank GenAI Trainee home task (2026).

## What it does

1. Ingests three PDF reports (Tallink Grupp 2024 sustainability report and two Eesti Energia 2025 reports).
2. Chunks them with page-number metadata, embeds them, and indexes them in FAISS.
3. For each company, runs a LangGraph workflow that produces:
   - a short document summary, and
   - grounded answers to five fixed ESG-style questions, each with source filename, page number, supporting quote, and a derived confidence level (high / medium / low).
4. Writes everything to `data/output/results.json`.
5. Ships a Streamlit UI that reads the JSON for review.

If the documents do not contain enough information to answer a question, the answer is returned with `"status": "not_found"` instead of being invented.

## Setup

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/mattiaspuhk/swedbank-rag.git
cd swedbank-rag
uv sync
cp .env.example .env
# edit .env and add your OPENAI_API_KEY
```

## Environment variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `OPENAI_API_KEY` | yes | — | Auth for chat completions and embeddings |
| `OPENAI_CHAT_MODEL` | no | `gpt-4o-mini` | Chat model |
| `OPENAI_EMBEDDING_MODEL` | no | `text-embedding-3-small` | Embedding model |

## Running

Generate the JSON artifact:

```bash
uv run rag-generate
```

Launch the Streamlit review UI:

```bash
uv run streamlit run app/streamlit_app.py
```

## Reports used

- Tallink Grupp Sustainability Report 2024 — `Tallink-Grupp-Sustainability-Report-2024-ENG-updated.pdf`
- Eesti Energia Annual Report 2025 (English) — `eesti-energia-2025-final-en.pdf`
- Eesti Energia SPO Use of Proceeds — `Eesti-SPO-UoP.pdf`

PDFs are committed to `data/raw/` so the project runs offline after `uv sync`.

## Model choice

_TBD — to be filled in once the pipeline is wired up. Will cover: which model, why, cost per run, privacy considerations, and observed performance._

## Assumptions

_TBD._

## Limitations

_TBD._

## Possible improvements

_TBD._
