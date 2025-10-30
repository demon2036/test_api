"""Test configurations for media & entertainment APIs

This package contains configuration files for various media APIs,
making it easy to add or modify test cases without touching the main test code.

Note: Open Library config removed as the test is deprecated.
"""

from .spotify_config import get_config as get_spotify_config, DEFAULT_ARTISTS
from .tmdb_config import get_config as get_tmdb_config, DEFAULT_PERSONS
from .youtube_config import get_config as get_youtube_config, DEFAULT_CHANNELS

__all__ = [
    'get_spotify_config',
    'get_tmdb_config',
    'get_youtube_config',
    'DEFAULT_ARTISTS',
    'DEFAULT_PERSONS',
    'DEFAULT_CHANNELS',
]
