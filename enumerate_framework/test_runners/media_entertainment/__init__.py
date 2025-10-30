"""Media & Entertainment API Tests

This package includes:
- Test modules: test_spotify, test_youtube, test_tmdb
- Shared utilities: media_utils (environment, auth, result building, display)
- Test configurations: test_configs/ (centralized test case definitions)
- Deprecated files: deprecated/ (original versions + deprecated test_openlibrary)
"""

# Import all test modules to make them available
from . import test_spotify
from . import test_youtube
from . import test_tmdb

__all__ = [
    'test_spotify',
    'test_youtube',
    'test_tmdb',
]
