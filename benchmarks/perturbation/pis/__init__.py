"""PIS: Probabilistic Inconsistency Signal for verifier-reliability analysis.

Experimental uncertainty evaluator for the perturbation benchmark (Issue #23).
Self-contained by design: does not import or modify the production verifier.
"""
# 0.1.1: parsing: repair invalid LaTeX backslash escapes in model JSON
#        (tracked, "repaired" status; identity on valid JSON).
#        runner: resume re-attempts previously failed examples; stale/duplicate
#        cache lines are dropped instead of being skipped; --force truncates.
__version__ = "0.1.1"