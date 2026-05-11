"""Smoke tests for the output JSON contract.

Verifies that the Pydantic models in :mod:`rag.schemas` round-trip
correctly against the structure required by the task spec, so that a
regression in the schema is caught before a full pipeline run.
"""
