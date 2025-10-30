"""TMDb API test configurations

Configuration for persons (actors/directors) to test with TMDb API.
"""

# Default test persons
DEFAULT_PERSONS = [
    {"id": 31, "name": "Tom Hanks"},
    {"id": 287, "name": "Brad Pitt"},
    {"id": 6193, "name": "Leonardo DiCaprio"},
]

# Additional persons for extended testing
EXTENDED_PERSONS = [
    # Add more actors/directors here as needed
]

def get_config(extended=False):
    """Get TMDb test configuration

    Args:
        extended: If True, include extended test persons

    Returns:
        dict: Configuration dictionary with 'persons' key
    """
    persons = DEFAULT_PERSONS.copy()
    if extended:
        persons.extend(EXTENDED_PERSONS)

    return {
        "persons": persons
    }
