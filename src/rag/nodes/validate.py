"""Evidence validation node and confidence derivation.

Checks that each cited quote actually appears in the retrieved chunks for
that question. Confidence is then derived from the match quality:

    verbatim substring match -> high
    fuzzy / paraphrase match -> medium
    no match found           -> low (and the answer is downgraded to
                                     ``not_found`` rather than emitted as
                                     an unsupported claim)

This step exists so the pipeline cannot silently hallucinate citations.
"""
