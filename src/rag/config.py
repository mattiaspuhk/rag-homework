"""Central configuration: paths, model names, and the document registry.

Everything that is environment- or input-dependent lives here so that the rest
of the codebase can stay free of literals. The document registry (PDFs to
ingest, with company name, year, and source URL) is the single source of
truth for what the pipeline processes.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, HttpUrl

# Loaded at import time so any module that imports from `rag.config` sees the
# OPENAI_API_KEY and model overrides without each module needing to call
# `load_dotenv()` itself.
load_dotenv()

# Project layout. Resolved relative to this file so the code works regardless
# of where the process is launched from.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
PDF_DIR = DATA_DIR / "pdfs"
INDEX_DIR = DATA_DIR / "index"
OUTPUT_DIR = DATA_DIR / "output"
OUTPUT_FILE = OUTPUT_DIR / "results.json"

# Models. Overridable via .env so we can swap to a cheaper model for dev runs
# without code changes.
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Chunking. Picked for prose-heavy ESG/annual reports: large enough that a
# chunk usually contains a full claim with its surrounding context, small
# enough that retrieved chunks fit comfortably in a 4-chunk prompt.
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


class DocumentSpec(BaseModel):
    """Static description of a single source PDF the pipeline must process."""

    company_name: str
    file_name: str
    source_url: HttpUrl
    report_year: str


# The three documents named in the task spec. Order is deterministic so the
# generated JSON artifact is stable across runs.
DOCUMENT_REGISTRY: list[DocumentSpec] = [
    DocumentSpec(
        company_name="Tallink Grupp",
        file_name="Tallink-Grupp-Sustainability-Report-2024-ENG-updated.pdf",
        source_url=(
            "https://image.tallink.com/image/upload/grupp/documents/"
            "sustainability-reports/"
            "Tallink-Grupp-Sustainability-Report-2024-ENG-updated.pdf"
        ),
        report_year="2024",
    ),
    DocumentSpec(
        company_name="Eesti Energia",
        file_name="eesti-energia-2025-final-en.pdf",
        source_url=(
            "https://public-docs.enefit.com/ettevottest/investorile/"
            "eesti-energia-2025-final-en.pdf"
        ),
        report_year="2025",
    ),
    DocumentSpec(
        company_name="Eesti Energia",
        file_name="Eesti-SPO-UoP.pdf",
        source_url=(
            "https://public-docs.enefit.ee/ettevottest/investorile/ESG/"
            "Eesti-SPO-UoP.pdf"
        ),
        report_year="2025",
    ),
]
