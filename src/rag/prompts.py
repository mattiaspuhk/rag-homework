"""Prompt templates for the summary and per-question answer steps.

Prompts are isolated here so they can be reviewed and tuned without
touching pipeline code. The grounding contract is enforced in the prompt
itself: the model is instructed to answer only from the provided context
and to return ``not_found`` rather than speculate.
"""
