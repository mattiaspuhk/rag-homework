"""Pydantic models that define the output JSON contract.

The schema mirrors the structure required by the task spec: per-company
results containing a document summary and a list of answered (or not-found)
questions, each with grounded evidence (page, quote, confidence). These
models are used both to constrain LLM structured output and to validate the
final artifact written to ``data/output/results.json``.
"""
