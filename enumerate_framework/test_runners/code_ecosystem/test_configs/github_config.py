"""GitHub API test configuration

This module contains test data for GitHub API tests, including users,
repositories, and configuration parameters.
"""

# Users for testing (mix of famous developers)
DEFAULT_USERS = [
    {"username": "torvalds", "name": "Linus Torvalds"},
    {"username": "gvanrossum", "name": "Guido van Rossum"},
    {"username": "tj", "name": "TJ Holowaychuk"},
    {"username": "sindresorhus", "name": "Sindre Sorhus"},
]

# Repositories for release/tag tests (projects with many releases)
DEFAULT_RELEASE_REPOS = [
    {"repo": "nodejs/node", "name": "Node.js"},
    {"repo": "python/cpython", "name": "Python"},
    {"repo": "rust-lang/rust", "name": "Rust"},
]

# Repositories for branch tests (projects with many branches)
DEFAULT_BRANCH_REPOS = [
    {"repo": "rails/rails", "name": "Ruby on Rails"},
    {"repo": "django/django", "name": "Django"},
    {"repo": "laravel/framework", "name": "Laravel"},
]


def get_config(max_items=100):
    """Get GitHub test configuration

    Args:
        max_items: Maximum items to fetch per API call

    Returns:
        dict: Configuration with 'users', 'release_repos', 'branch_repos', and 'max_items'
    """
    return {
        "users": DEFAULT_USERS.copy(),
        "release_repos": DEFAULT_RELEASE_REPOS.copy(),
        "branch_repos": DEFAULT_BRANCH_REPOS.copy(),
        "max_items": max_items
    }
