"""LangGraph workflow definition.

Wires the pipeline as an explicit graph:

    ingest -> retrieve -> answer -> validate -> assemble

Each node lives in :mod:`rag.nodes` and operates on a shared state
object. The graph runs once per company; the assemble step writes the
combined per-company results into the final JSON artifact.
"""
