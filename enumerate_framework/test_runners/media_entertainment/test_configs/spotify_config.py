"""Spotify API test configurations

Configuration for artists to test with the Spotify API.
"""

# Default test artists
DEFAULT_ARTISTS = [
    {"id": "2c32JruIkUyfdycHmhIph4", "name": "花譜 (KAF)"},
    {"id": "1rFELoNfdLOYWPwtrBN6zS", "name": "理芽 (RIM)"},
]

# Additional artists for extended testing
EXTENDED_ARTISTS = [
    # Add more artists here as needed
]

def get_config(extended=False):
    """Get Spotify test configuration

    Args:
        extended: If True, include extended test artists

    Returns:
        dict: Configuration dictionary with 'artists' key
    """
    artists = DEFAULT_ARTISTS.copy()
    if extended:
        artists.extend(EXTENDED_ARTISTS)

    return {
        "artists": artists
    }
