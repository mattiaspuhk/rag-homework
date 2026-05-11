"""Streamlit review UI.

Reads ``data/output/results.json`` and renders, for each company: the
document summary, the five answered (or not-found) questions, the
confidence level for each, and the supporting page-level quotes. The UI
deliberately does not call the LLM directly — the JSON file is the
single source of truth for what is shown.
"""
