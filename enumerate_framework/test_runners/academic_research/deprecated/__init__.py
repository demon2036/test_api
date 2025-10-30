"""
Deprecated academic research test runners.

These files are no longer actively maintained and have been moved here for reference only.
For active development, please use the DBLP test runner in the parent directory.
"""

from .pubmed import run as run_pubmed
from .zenodo import run as run_zenodo

__all__ = ['run_pubmed', 'run_zenodo']
