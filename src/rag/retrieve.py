"""Vector store construction and retrieval.

Builds a per-company FAISS index from the chunks produced by :mod:`ingest`
and exposes a retriever interface used by the answer node. FAISS is kept
in-memory and rebuilt on each run — the corpus is small (three PDFs) and
this keeps the pipeline reproducible with no on-disk state to invalidate.
"""
