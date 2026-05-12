"""Per-document retrieval against the shared FAISS index.

The FAISS index built in :mod:`rag.ingest` contains chunks from every PDF
in the registry. Each chunk carries ``file_name`` in its metadata, and
this module exposes retrieval primitives that filter by that field so a
company entry's answers only cite evidence from its own document — even
when two entries share a ``company_name`` (as Eesti Energia does).
"""

from __future__ import annotations

import logging

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from rag.config import DocumentSpec

logger = logging.getLogger(__name__)

DEFAULT_K = 5
# FAISS applies metadata filters *after* the vector search, so the top-k by
# similarity may contain chunks from other documents that get filtered out.
# Over-fetch the candidate pool to make sure we still end up with k chunks
# from the target document.
_FETCH_MULTIPLIER = 4


def retrieve(
    store: FAISS,
    spec: DocumentSpec,
    query: str,
    k: int = DEFAULT_K,
) -> list[Document]:
    """Return the top-``k`` chunks from ``spec``'s PDF most relevant to ``query``."""
    return store.similarity_search(
        query,
        k=k,
        fetch_k=k * _FETCH_MULTIPLIER,
        filter={"file_name": spec.file_name},
    )


def make_retriever(
    store: FAISS,
    spec: DocumentSpec,
    k: int = DEFAULT_K,
) -> BaseRetriever:
    """Return a LangChain Retriever scoped to ``spec``'s PDF.

    Useful for plugging into LangGraph nodes that expect a Runnable
    retriever (``retriever.invoke(query)``) rather than calling
    :func:`retrieve` directly.
    """
    return store.as_retriever(
        search_kwargs={
            "k": k,
            "fetch_k": k * _FETCH_MULTIPLIER,
            "filter": {"file_name": spec.file_name},
        }
    )
