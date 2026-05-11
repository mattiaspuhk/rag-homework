"""PDF loading and chunking.

Reads each PDF from ``data/raw/``, extracts text page-by-page so that page
numbers survive into chunk metadata, and splits the text into overlapping
chunks suitable for embedding. Page-level metadata is load-bearing — every
downstream answer must be able to cite the page the evidence came from.
"""
