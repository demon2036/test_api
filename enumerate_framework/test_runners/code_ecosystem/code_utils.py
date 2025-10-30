"""Code Ecosystem test runners utility functions

This module contains reusable functions to simplify code ecosystem test code
and enable parameter reuse. Follows the pattern established by media_utils.py.
"""

try:
    # When imported as part of the enumerate framework package structure
    from ..utils import create_test_result
except ImportError:  # pragma: no cover - fallback for direct script execution
    from test_runners.utils import create_test_result


# ============= Config Management =============

def merge_test_config(default_config, user_config):
    """Merge user configuration with default configuration

    Args:
        default_config: Default configuration dictionary
        user_config: User-provided configuration dictionary (or None)

    Returns:
        dict: Merged configuration
    """
    if not user_config:
        return default_config.copy()

    merged = default_config.copy()
    merged.update(user_config)
    return merged


def load_package_config(ecosystem, extended=False):
    """Load package configuration for a specific ecosystem

    Args:
        ecosystem: Name of the package ecosystem (e.g., 'npm', 'pypi')
        extended: If True, include extended test packages from TODO

    Returns:
        dict: Configuration with 'packages' list
    """
    try:
        from .test_configs.package_config import get_config
        return get_config(ecosystem, extended=extended)
    except ImportError:
        # Fallback to defaults if config not available
        defaults = {
            "npm": ["react"],
            "pypi": ["requests"],
            "crates": ["serde"],
            "rubygems": ["rails"],
            "nuget": ["Newtonsoft.Json"],
            "go_proxy": ["github.com/gin-gonic/gin"],
            "conda": ["numpy"],
            "cran": ["ggplot2"],
        }
        packages = [defaults.get(ecosystem, [])]
        return {"packages": packages}


# ============= Display Functions =============

def print_section_header(title, identifier=None, width=70):
    """Print a formatted section header

    Args:
        title: Main title text
        identifier: Optional identifier (e.g., package name)
        width: Width of the separator line
    """
    print(f"\n{'='*width}")
    if identifier:
        print(f"{title}: {identifier}")
    else:
        print(title)
    print(f"{'='*width}")


def print_test_header(test_number, total_tests, description):
    """Print a formatted test header

    Args:
        test_number: Current test number (e.g., 1)
        total_tests: Total number of tests (e.g., 5)
        description: Test description
    """
    print(f"\n[增强问题 {test_number}/{total_tests}] {description}")


def print_filter_stats(filtered_count, total_count, label="✓ 找到"):
    """Print filter statistics with percentage

    Args:
        filtered_count: Number of items after filtering
        total_count: Total number of items before filtering
        label: Label prefix for the output
    """
    percentage = calculate_percentage(filtered_count, total_count)
    print(f"  {label} {filtered_count} 个版本（占比: {percentage:.1f}%）")


def print_version_preview(versions, max_items=5, format_func=None):
    """Print a preview of version list

    Args:
        versions: List of version dictionaries
        max_items: Maximum number of items to display
        format_func: Optional function to format each version (receives version dict)
    """
    if not versions:
        return

    for v in versions[:max_items]:
        if format_func:
            output = format_func(v)
        else:
            # Default format: version + time
            time_str = v.get('publish_time', v.get('upload_time', ''))[:10] if v.get('publish_time') or v.get('upload_time') else 'Unknown'
            output = f"    - {v['version']} ({time_str})"
        print(output)

    if len(versions) > max_items:
        print(f"    ... 还有{len(versions) - max_items}个版本")


def calculate_percentage(filtered_count, total_count):
    """Calculate percentage safely

    Args:
        filtered_count: Number of filtered items
        total_count: Total number of items

    Returns:
        float: Percentage (0.0 if total_count is 0)
    """
    return (filtered_count / total_count * 100) if total_count > 0 else 0.0


# ============= Result Building =============

def build_base_result(question, versions, api_info=None, **metadata):
    """Build a standardized base test result structure

    Args:
        question: Base question text
        versions: List of version dictionaries that already use the ``answer`` key
        api_info: Optional API metadata dictionary
        **metadata: Additional contextual fields to attach to the result

    Returns:
        dict: Base result structure matching the ``create_test_result`` schema
    """
    return create_test_result(
        question=question,
        answers=versions,
        api_info=api_info,
        **metadata
    )


def build_enhanced_result(question, filtered_versions, api_info=None,
                          format_func=None, **metadata):
    """Build an enhanced test result structure using the standard schema

    Args:
        question: Question text
        filtered_versions: List of filtered version dictionaries
        api_info: Optional API metadata dictionary
        format_func: Optional function to format version data
        **metadata: Additional contextual fields to attach to the result

    Returns:
        dict: Enhanced result structure
    """
    if format_func:
        answers = [format_func(v) for v in filtered_versions]
    else:
        answers = filtered_versions

    return create_test_result(
        question=question,
        answers=answers,
        api_info=api_info,
        **metadata
    )


def format_version_basic(version_dict):
    """Format version with basic info (version + time)

    Args:
        version_dict: Version dictionary with metadata

    Returns:
        dict: Formatted version data
    """
    time_key = 'publish_time' if 'publish_time' in version_dict else 'upload_time'
    time_value = version_dict.get(time_key)

    return {
        "answer": version_dict['version'],
        time_key: time_value[:10] if time_value else None
    }


def build_package_summary(version_counts):
    """Build a summary of version counts for a package

    Args:
        version_counts: Dictionary with count keys (e.g., {'total_versions': 100, ...})

    Returns:
        dict: Summary structure
    """
    return version_counts


# ============= Common Test Runners =============

def run_year_filter_test(fetcher, versions_with_metadata, year, package_name,
                        ecosystem_name):
    """Run a year filter test

    Args:
        fetcher: Fetcher instance with filter_by_year method
        versions_with_metadata: List of version dictionaries
        year: Year to filter by
        package_name: Name of the package
        ecosystem_name: Name of the ecosystem (e.g., 'NPM', 'PyPI')

    Returns:
        dict: Enhanced result structure
    """
    filtered_versions = fetcher.filter_by_year(versions_with_metadata, year)

    question = f"列出{ecosystem_name}上{package_name}包在{year}年发布的所有版本"

    return build_enhanced_result(
        question=question,
        filtered_versions=filtered_versions,
        format_func=format_version_basic,
        package=package_name,
        ecosystem=ecosystem_name,
        filter=f"year={year}"
    )


def run_prerelease_filter_test(fetcher, versions_with_metadata, package_name,
                               ecosystem_name):
    """Run a prerelease filter test

    Args:
        fetcher: Fetcher instance with filter_prerelease_versions method
        versions_with_metadata: List of version dictionaries
        package_name: Name of the package
        ecosystem_name: Name of the ecosystem

    Returns:
        dict: Enhanced result structure
    """
    prerelease_versions = fetcher.filter_prerelease_versions(versions_with_metadata)

    question = f"列出{ecosystem_name}上{package_name}包的所有预发布版本"

    return build_enhanced_result(
        question=question,
        filtered_versions=prerelease_versions,
        format_func=format_version_basic,
        package=package_name,
        ecosystem=ecosystem_name,
        filter="include_prerelease=True"
    )


def run_stable_filter_test(fetcher, versions_with_metadata, package_name,
                          ecosystem_name, limit=20):
    """Run a stable versions filter test

    Args:
        fetcher: Fetcher instance with filter_stable_versions method
        versions_with_metadata: List of version dictionaries
        package_name: Name of the package
        ecosystem_name: Name of the ecosystem
        limit: Maximum number of versions to include in result

    Returns:
        dict: Enhanced result structure
    """
    stable_versions = fetcher.filter_stable_versions(versions_with_metadata)

    question = f"列出{ecosystem_name}上{package_name}包的所有稳定版本"

    # Limit results to save space
    limited_versions = stable_versions[:limit]

    return build_enhanced_result(
        question=question,
        filtered_versions=limited_versions,
        format_func=format_version_basic,
        package=package_name,
        ecosystem=ecosystem_name,
        filter="exclude_prerelease=True"
    )


# ============= Format Helpers =============

def format_version_with_time(version_dict):
    """Format version for display with time

    Args:
        version_dict: Version dictionary with metadata

    Returns:
        str: Formatted string
    """
    time_key = 'publish_time' if 'publish_time' in version_dict else 'upload_time'
    time_value = version_dict.get(time_key)
    time_str = time_value[:10] if time_value else 'Unknown'

    return f"    - {version_dict['version']} ({time_str})"


def format_npm_version_with_maintainer(version_dict):
    """Format NPM version with maintainer info

    Args:
        version_dict: Version dictionary with metadata

    Returns:
        str: Formatted string
    """
    time_str = version_dict.get('publish_time', '')[:10] if version_dict.get('publish_time') else 'Unknown'
    maintainers = version_dict.get('maintainers', [])
    maintainer_str = f" (by {maintainers[0]})" if maintainers else ""

    return f"    - {version_dict['version']} ({time_str}){maintainer_str}"


def format_pypi_version_with_wheel(version_dict):
    """Format PyPI version with wheel indicator

    Args:
        version_dict: Version dictionary with metadata

    Returns:
        str: Formatted string
    """
    wheel_indicator = "🔧" if version_dict.get('has_wheel') else "📦"
    time_str = version_dict.get('upload_time', '')[:10] if version_dict.get('upload_time') else 'Unknown'

    return f"    - {version_dict['version']} {wheel_indicator} ({time_str})"


def format_crates_version_with_downloads(version_dict):
    """Format Crates version with download count

    Args:
        version_dict: Version dictionary with metadata

    Returns:
        str: Formatted string
    """
    downloads = version_dict.get('downloads', 0)
    time_str = version_dict.get('created_at', '')[:10] if version_dict.get('created_at') else 'Unknown'

    return f"    - {version_dict['version']} ({time_str}, {downloads:,} downloads)"
