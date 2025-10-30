"""Academic Research API Tests

Active test runners:
- dblp: DBLP API test runner (modularized, actively maintained)

Deprecated test runners (see deprecated/ folder):
- pubmed: PubMed API test runner (deprecated, moved to deprecated/)
- zenodo: Zenodo API test runner (deprecated, moved to deprecated/)
"""

# Active test modules
from . import dblp

# Deprecated test modules (for backward compatibility)
from .deprecated import run_pubmed, run_zenodo

__all__ = [
    'dblp',
    'run_pubmed',  # deprecated
    'run_zenodo',  # deprecated
]
