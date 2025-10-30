"""Media & Entertainment test runners utility functions

This module contains reusable functions to simplify media entertainment test code
and enable parameter reuse. Follows the pattern established by dblp_utils.py.
"""

import os
from pathlib import Path


# ============= Environment & Authentication Management =============

def load_env_file():
    """Load .env file from project root if available"""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    # Load from current working directory
    load_dotenv()

    # Also try to load from project root
    project_env = Path(__file__).resolve().parents[3] / ".env"
    if project_env.exists():
        load_dotenv(project_env)


def check_api_credentials(required_keys, api_name, get_url=""):
    """Generic API credential checker

    Args:
        required_keys: List of environment variable names required
        api_name: Name of the API for display
        get_url: URL where users can get credentials

    Returns:
        tuple: (bool, str) - (credentials_exist, skip_message)
    """
    missing = [key for key in required_keys if not os.getenv(key)]

    if missing:
        message = f"\n⚠️  跳过{api_name}测试 - 缺少API凭据"
        message += f"\n   请在.env文件中设置: {', '.join(missing)}"
        if get_url:
            message += f"\n   获取方式: {get_url}"
        return False, message

    return True, ""


def check_spotify_credentials():
    """Check Spotify API credentials

    Returns:
        tuple: (bool, str) - (credentials_exist, skip_message)
    """
    return check_api_credentials(
        ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET'],
        'Spotify',
        'https://developer.spotify.com/dashboard'
    )


def check_tmdb_credentials():
    """Check TMDb API credentials

    Returns:
        tuple: (bool, str) - (credentials_exist, skip_message)
    """
    return check_api_credentials(
        ['TMDB_API_KEY'],
        'TMDb',
        'https://www.themoviedb.org/settings/api'
    )


def check_youtube_credentials():
    """Check YouTube API credentials

    Returns:
        tuple: (bool, str) - (credentials_exist, skip_message)
    """
    return check_api_credentials(
        ['YOUTUBE_API_KEY'],
        'YouTube',
        'https://console.cloud.google.com/apis/credentials'
    )


# ============= Config Management =============

def merge_test_config(default_config, user_config):
    """Merge user configuration with default configuration

    Args:
        default_config: Default configuration dictionary
        user_config: User-provided configuration dictionary (or None)

    Returns:
        dict: Merged configuration
    """
    config = default_config.copy()
    if user_config:
        config.update(user_config)
    return config


def load_test_config(api_name, extended=False, **kwargs):
    """Load test configuration from test_configs package

    Args:
        api_name: Name of the API (spotify, tmdb, youtube)
        extended: Whether to use extended test set
        **kwargs: Additional arguments to pass to get_config()

    Returns:
        dict: Configuration dictionary
    """
    try:
        if api_name == 'spotify':
            from .test_configs import get_spotify_config
            return get_spotify_config(extended=extended)
        elif api_name == 'tmdb':
            from .test_configs import get_tmdb_config
            return get_tmdb_config(extended=extended)
        elif api_name == 'youtube':
            from .test_configs import get_youtube_config
            return get_youtube_config(extended=extended, **kwargs)
        else:
            raise ValueError(f"Unknown API: {api_name}")
    except ImportError as e:
        raise ImportError(f"Failed to load config for {api_name}: {e}")


# ============= Result Building =============

def build_base_result(identifier, name, api_info, tests):
    """Build a standardized base result dictionary

    Args:
        identifier: Unique identifier (artist_id, person_id, channel_id, etc.)
        name: Display name
        api_info: API information dictionary
        tests: List of test results

    Returns:
        dict: Standardized result structure
    """
    # Determine the identifier key name based on common patterns
    if "artist" in str(identifier) or len(identifier) == 22:  # Spotify artist ID length
        id_key = "artist_id"
        name_key = "artist_name"
    elif "channel" in str(identifier) or identifier.startswith("UC"):  # YouTube channel
        id_key = "channel_id"
        name_key = "channel_name"
    elif isinstance(identifier, int):  # TMDb uses integer IDs
        id_key = "person_id"
        name_key = "person_name"
    elif identifier.startswith("OL"):  # Open Library author key
        id_key = "author_key"
        name_key = "author_name"
    else:
        id_key = "identifier"
        name_key = "name"

    return {
        id_key: identifier,
        name_key: name,
        "api_info": api_info,
        "tests": tests
    }


def build_test_result(question, total, items, metadata_fields=None):
    """Build a standardized test result

    Args:
        question: Question description
        total: Total count of items
        items: List of items (can be raw or pre-formatted)
        metadata_fields: Optional list of metadata field names to highlight

    Returns:
        dict: Test result structure
    """
    result = {
        "question": question,
        "total": total,
        "all_items": items
    }

    if metadata_fields:
        result["metadata_fields"] = metadata_fields

    return result


def format_item_with_metadata(item, fields, index=None):
    """Format an item by extracting specified fields

    Args:
        item: Item dictionary or object
        fields: List of field names to extract
        index: Optional index/rank number (1-based)

    Returns:
        dict: Formatted item with selected fields
    """
    formatted = {}

    if index is not None:
        formatted["rank"] = index

    for field in fields:
        # Support nested field access with dot notation
        if '.' in field:
            parts = field.split('.')
            value = item
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    value = getattr(value, part, None)
                if value is None:
                    break
            formatted[field.replace('.', '_')] = value
        else:
            if isinstance(item, dict):
                formatted[field] = item.get(field)
            else:
                formatted[field] = getattr(item, field, None)

    return formatted


# ============= Display Functions =============

def print_section_header(title, identifier, width=60):
    """Print a section header with separator lines

    Args:
        title: Section title (e.g., "测试艺术家")
        identifier: Identifier to display
        width: Width of separator line
    """
    print(f"\n{'='*width}")
    print(f"{title}: {identifier}")
    print(f"{'='*width}")


def print_test_info(test_number, question, total, show_percentage=False, filtered=None):
    """Print test information header

    Args:
        test_number: Test number or label (e.g., "[1]" or "[2a]")
        question: Question text
        total: Total count
        show_percentage: Whether to show percentage (requires filtered count)
        filtered: Filtered count (for percentage calculation)
    """
    print(f"\n{test_number} {question}")
    if show_percentage and filtered is not None:
        percentage = (filtered / total * 100) if total > 0 else 0
        print(f"  ✓ 总计: {filtered} / {total} ({percentage:.1f}%)")
    else:
        print(f"  ✓ 总计: {total}")


def print_item_preview(items, max_items=3, format_func=None, indent="    "):
    """Print a preview of items

    Args:
        items: List of items to preview
        max_items: Maximum number of items to show
        format_func: Optional function to format each item for display
        indent: Indentation string
    """
    if not items:
        print(f"{indent}(无结果)")
        return

    print(f"  完整列表" + (f"（前{max_items}项）:" if len(items) > max_items else ":"))

    for i, item in enumerate(items[:max_items], 1):
        if format_func:
            display_text = format_func(item)
        elif isinstance(item, dict):
            # Default formatting for dict items
            display_text = str(item)
        else:
            display_text = str(item)

        print(f"{indent}{i}. {display_text}")


def print_statistics(label, filtered_count, total_count, show_percentage=True):
    """Print filter statistics

    Args:
        label: Label text (e.g., "找到", "筛选出")
        filtered_count: Number of filtered items
        total_count: Total number of items
        show_percentage: Whether to show percentage
    """
    if show_percentage and total_count > 0:
        percentage = (filtered_count / total_count * 100)
        print(f"  ✓ {label}: {filtered_count} / {total_count} ({percentage:.1f}%)")
    else:
        print(f"  ✓ {label}: {filtered_count}")


# ============= Test Execution Helpers =============

def run_filter_test(fetcher, items, filter_method_name, filter_args,
                   question, test_number, format_func=None,
                   total_count=None, show_preview=True):
    """Generic function to run a filter test and return results

    Args:
        fetcher: Fetcher instance with filter methods
        items: List of items to filter
        filter_method_name: Name of the filter method to call
        filter_args: Arguments to pass to the filter method
        question: Question text
        test_number: Test number label
        format_func: Optional function to format items for display
        total_count: Total count for percentage calculation
        show_preview: Whether to print preview

    Returns:
        dict: Test result dictionary
    """
    print_test_info(test_number, question, len(items) if total_count is None else total_count)

    # Get the filter method
    filter_method = getattr(fetcher, filter_method_name)

    # Execute filter
    if isinstance(filter_args, dict):
        filtered = filter_method(items, **filter_args)
    elif isinstance(filter_args, (list, tuple)):
        filtered = filter_method(items, *filter_args)
    else:
        filtered = filter_method(items, filter_args)

    # Print statistics
    if total_count is None:
        total_count = len(items)
    print_statistics("找到", len(filtered), total_count)

    # Print preview
    if show_preview:
        print_item_preview(filtered, format_func=format_func)

    # Build result
    if format_func:
        formatted_items = [format_func(item) for item in filtered]
    else:
        formatted_items = filtered

    return build_test_result(question, len(filtered), formatted_items)


def create_skip_result(api_name, auth_type, config, reason):
    """Create a standardized skip result for APIs without credentials

    Args:
        api_name: Name of the API
        auth_type: Authentication type (e.g., "API Key", "OAuth 2.0")
        config: Configuration dictionary
        reason: Reason for skipping

    Returns:
        dict: Skip result dictionary
    """
    return {
        "api_name": api_name,
        "requires_auth": True,
        "auth_type": auth_type,
        "status": "skipped",
        "reason": reason,
        "config": config,
        "tests": []
    }
