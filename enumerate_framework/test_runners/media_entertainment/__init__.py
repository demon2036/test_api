"""Media & Entertainment API Tests"""

# Import all test modules to make them available
from . import test_spotify
from . import test_youtube
from . import test_tmdb
from . import test_openlibrary

__all__ = [
    'test_spotify',
    'test_youtube',
    'test_tmdb',
    'test_openlibrary',
]
