"""Test configurations for code ecosystem tests"""

from .package_config import get_config, DEFAULT_PACKAGES, EXTENDED_PACKAGES
from .github_config import (
    get_config as get_github_config,
    DEFAULT_USERS,
    DEFAULT_RELEASE_REPOS,
    DEFAULT_BRANCH_REPOS
)

__all__ = [
    'get_config',
    'DEFAULT_PACKAGES',
    'EXTENDED_PACKAGES',
    'get_github_config',
    'DEFAULT_USERS',
    'DEFAULT_RELEASE_REPOS',
    'DEFAULT_BRANCH_REPOS'
]
