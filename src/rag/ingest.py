"""PDF loading, chunking, embedding, and vector store construction.

Reads each PDF from ``data/pdfs/`` (downloading any that are missing),
extracts text page-by-page so that page numbers survive into chunk
metadata, splits the text into overlapping chunks, embeds them with
OpenAI embeddings, and persists a FAISS index under ``data/index/``.

The module is idempotent: if a saved index exists, it is loaded instead
of being rebuilt. To force a rebuild, delete ``data/index/`` or pass
``force_rebuild=True`` to :func:`build_or_load_vectorstore`.

Page-level metadata is load-bearing — every downstream answer must be
able to cite the file and page the evidence came from.
"""

from __future__ import annotations

import logging
from pathlib import Path

import httpx
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DOCUMENT_REGISTRY,
    INDEX_DIR,
    OPENAI_EMBEDDING_MODEL,
    PDF_DIR,
    DocumentSpec,
)

logger = logging.getLogger(__name__)

_DOWNLOAD_TIMEOUT_SECONDS = 60.0


def download_pdfs(
    specs: list[DocumentSpec] = DOCUMENT_REGISTRY,
    dest_dir: Path = PDF_DIR,
) -> None:
    """Download any PDFs in ``specs`` that aren't already on disk.

    Existing files are left untouched — this is what makes a fresh clone
    "just work" while not re-downloading on every run for developers who
    already have the PDFs locally.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        target = dest_dir / spec.file_name
        if target.exists():
            logger.debug("PDF already present, skipping download: %s", target.name)
            continue
        logger.info("Downloading %s", spec.file_name)
        # Stream to disk so we don't hold the whole PDF in memory; some of
        # these reports are 100+ pages.
        with httpx.stream(
            "GET",
            str(spec.source_url),
            follow_redirects=True,
            timeout=_DOWNLOAD_TIMEOUT_SECONDS,
        ) as response:
            response.raise_for_status()
            with target.open("wb") as out_file:
                for chunk in response.iter_bytes():
                    out_file.write(chunk)


def load_and_chunk(
    specs: list[DocumentSpec] = DOCUMENT_REGISTRY,
    pdf_dir: Path = PDF_DIR,
) -> list[Document]:
    """Load each PDF page-by-page and split into overlapping chunks.

    Each returned chunk carries metadata identifying its company, source
    file, source URL, report year, and 1-indexed page number — everything
    the answer/validate nodes need to build a :class:`rag.schemas.Source`.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        # Prefer splitting on paragraph and sentence boundaries before falling
        # back to whitespace — keeps quotes intact for citation.
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: list[Document] = []
    for spec in specs:
        path = pdf_dir / spec.file_name
        if not path.exists():
            raise FileNotFoundError(
                f"PDF not found: {path}. Call download_pdfs() or commit the file."
            )

        # PyPDFLoader yields one Document per page with metadata={'source', 'page'}
        # where 'page' is 0-indexed. We overwrite the metadata with our normalized
        # shape so downstream code doesn't have to remember loader-specific quirks.
        pages = PyPDFLoader(str(path)).load()
        for page_doc in pages:
            zero_indexed_page = int(page_doc.metadata.get("page", 0))
            page_doc.metadata = {
                "company_name": spec.company_name,
                "file_name": spec.file_name,
                "source_url": str(spec.source_url),
                "report_year": spec.report_year,
                "page": zero_indexed_page + 1,
            }

        chunks = splitter.split_documents(pages)
        logger.info("Loaded %s -> %d pages, %d chunks", spec.file_name, len(pages), len(chunks))
        all_chunks.extend(chunks)

    return all_chunks


def build_or_load_vectorstore(
    specs: list[DocumentSpec] = DOCUMENT_REGISTRY,
    pdf_dir: Path = PDF_DIR,
    index_dir: Path = INDEX_DIR,
    *,
    force_rebuild: bool = False,
) -> FAISS:
    """Return a FAISS store, loading from disk if a saved index exists.

    On the first run (or when ``force_rebuild=True``) this downloads any
    missing PDFs, chunks them, embeds the chunks via OpenAI, builds a
    FAISS index, and persists it under ``index_dir``. On subsequent runs
    the saved index is loaded without re-embedding — which is the whole
    point of the cache, since embedding the full corpus on every run
    would burn API calls for no benefit.
    """
    embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)

    index_file = index_dir / "index.faiss"
    if index_file.exists() and not force_rebuild:
        logger.info("Loading FAISS index from %s", index_dir)
        # FAISS.load_local uses pickle under the hood; the flag opts in to that
        # explicitly. Safe here because we only ever load an index we wrote
        # ourselves to a local path under the project tree.
        return FAISS.load_local(
            str(index_dir),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    download_pdfs(specs, pdf_dir)
    chunks = load_and_chunk(specs, pdf_dir)
    logger.info("Building FAISS index over %d chunks", len(chunks))
    store = FAISS.from_documents(chunks, embeddings)

    index_dir.mkdir(parents=True, exist_ok=True)
    store.save_local(str(index_dir))
    logger.info("Saved FAISS index to %s", index_dir)
    return store
