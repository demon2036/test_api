"""Media & Entertainment相关API获取器"""

from .spotify import SpotifyFetcher
from .youtube import YouTubeFetcher
from .tmdb import TMDbFetcher
from .imdb import IMDbFetcher
from .goodreads import OpenLibraryFetcher

__all__ = [
    'SpotifyFetcher',
    'YouTubeFetcher',
    'TMDbFetcher',
    'IMDbFetcher',
    'OpenLibraryFetcher',
]
