"""Per-question answer node.

For each of the five fixed questions, retrieves the most relevant chunks
for that company and asks the LLM to answer using only that context. The
node returns a structured ``AnswerEvidence`` object (see :mod:`schemas`)
including the supporting quote and page number, or marks the question as
``not_found`` when the context is insufficient.
"""
