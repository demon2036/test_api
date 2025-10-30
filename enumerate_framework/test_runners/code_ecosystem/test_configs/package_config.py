"""Package configurations for code ecosystem tests

This module contains package lists for each ecosystem.
"""

# Packages for testing (includes all packages from TODO.md)
DEFAULT_PACKAGES = {
    "npm": ["react", "vue"],
    "pypi": ["requests", "django"],
    "crates": ["serde", "rand"],
    "rubygems": ["rails", "jekyll"],
    "nuget": ["Newtonsoft.Json", "NUnit"],
    "go_proxy": ["github.com/gin-gonic/gin", "google.golang.org/grpc"],
    "conda": ["numpy", "pandas"],
    "cran": ["ggplot2", "dplyr"],
    "homebrew": ["python", "node", "git", "go"],
}

# Extended package lists for larger enumerations (placeholder)
EXTENDED_PACKAGES = DEFAULT_PACKAGES


def get_config(ecosystem, extended=False):
    """Get package configuration for a specific ecosystem

    Args:
        ecosystem: Name of the package ecosystem (e.g., 'npm', 'pypi')
        extended: If True, use extended package list (currently same as default)

    Returns:
        dict: Configuration with 'packages' list

    Examples:
        >>> get_config('npm')
        {'packages': ['react', 'vue']}

        >>> get_config('pypi')
        {'packages': ['requests', 'django']}
    """
    packages = []

    # Select package source based on extended flag
    package_source = EXTENDED_PACKAGES if extended else DEFAULT_PACKAGES

    if ecosystem in package_source:
        packages_data = package_source[ecosystem]
        if isinstance(packages_data, list):
            packages.extend(packages_data)
        else:
            packages.append(packages_data)

    return {"packages": packages}


def get_all_packages(ecosystem):
    """Get all packages for an ecosystem

    Args:
        ecosystem: Name of the package ecosystem

    Returns:
        list: List of all packages
    """
    return get_config(ecosystem)["packages"]
