"""YouTube API test configurations

Configuration for channels to test with YouTube API.
"""

# Default test channels
DEFAULT_CHANNELS = [
    {"id": "UCQ1U65-CQdIoZ2_NA4Z4F7A", "name": "花譜 / KAF (官方频道)"},
    {"id": "UCfBkUgaJ6eqYA9_TX2cmq9A", "name": "理芽 -RIM- (官方频道)"},
]

# Additional channels for extended testing
EXTENDED_CHANNELS = [
    {"id": "UCAOhUv73jM5iCpOhuJOQzxA", "name": "KAMITSUBAKI STUDIO"},
    # Add more channels here as needed
]

def get_config(extended=False, max_videos=200):
    """Get YouTube test configuration

    Args:
        extended: If True, include extended test channels
        max_videos: Maximum number of videos to fetch per channel

    Returns:
        dict: Configuration dictionary with 'channels' and 'max_videos' keys
    """
    channels = DEFAULT_CHANNELS.copy()
    if extended:
        channels.extend(EXTENDED_CHANNELS)

    return {
        "channels": channels,
        "max_videos": max_videos
    }
