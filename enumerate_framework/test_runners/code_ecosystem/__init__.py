"""Code Ecosystem API Tests"""

# Import all test modules to make them available
from . import (
    test_npm,
    test_pypi,
    test_github,
    test_crates,
    test_rubygems,
    test_nuget,
    test_go_proxy,
    test_conda,
    test_cran,
    test_homebrew,
)

__all__ = [
    'test_npm',
    'test_pypi',
    'test_github',
    'test_crates',
    'test_rubygems',
    'test_nuget',
    'test_go_proxy',
    'test_conda',
    'test_cran',
    'test_homebrew',
]
