"""CLI entry point for the JSON generation pipeline.

Loads environment variables, iterates over the document registry from
:mod:`config`, runs the LangGraph workflow for each company, and writes
the combined results to ``data/output/results.json``. Exposed as the
``rag-generate`` console script in pyproject.toml.
"""


def main() -> None:
    """Run the full ingest -> retrieve -> answer -> validate -> emit pipeline."""
    raise NotImplementedError
