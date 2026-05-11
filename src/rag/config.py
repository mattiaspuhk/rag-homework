"""Central configuration: paths, model names, and the document registry.

Everything that is environment- or input-dependent lives here so that the rest
of the codebase can stay free of literals. The document registry (PDFs to
ingest, with company name, year, and source URL) is the single source of
truth for what the pipeline processes.
"""
