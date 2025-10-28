"""YouTube Data API Fetcher"""

import requests
import os
from typing import List, Dict, Tuple
from .base import BaseFetcher


class YouTubeFetcher(BaseFetcher):
    """YouTube频道视频获取器"""

    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')

    def fetch_videos(self, channel_id: str, api_key: str = None, max_videos: int = 1000) -> Tuple[List[str], Dict, str]:
        """获取频道的所有视频"""
        # 使用传入的api_key或环境变量
        api_key = api_key or self.api_key
        if not api_key:
            print("  ✗ 需要YouTube API Key。请在.env中设置YOUTUBE_API_KEY或作为参数传入")
            return [], {}, ""

        api_url = "https://www.googleapis.com/youtube/v3/search"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {
                "part": "snippet",
                "channelId": channel_id,
                "maxResults": 50,
                "order": "date",
                "type": "video",
                "pageToken": "paginated"
            },
            "authentication": "Required (API Key)",
            "rate_limit": "10,000 quota units per day",
            "documentation": "https://developers.google.com/youtube/v3/docs/search/list"
        }

        videos = []
        page_token = None

        try:
            while len(videos) < max_videos:
                params = {
                    "part": "snippet",
                    "channelId": channel_id,
                    "maxResults": 50,
                    "order": "date",
                    "type": "video",
                    "key": api_key
                }
                if page_token:
                    params["pageToken"] = page_token

                response = requests.get(api_url, params=params, timeout=10)
                if response.status_code != 200:
                    break

                data = response.json()
                items = data.get('items', [])
                if not items:
                    break

                videos.extend([
                    f"{item['snippet']['title']} ({item['snippet']['publishedAt'][:10]})"
                    for item in items
                ])

                page_token = data.get('nextPageToken')
                if not page_token:
                    break

            question = f"列出YouTube频道 {channel_id} 的所有视频"
            return videos[:max_videos], api_info, question
        except Exception as e:
            print(f"  ✗ YouTube API错误 ({channel_id}): {e}")

        return [], api_info, ""

    def fetch_playlists(self, channel_id: str, api_key: str, max_playlists: int = 1000) -> Tuple[List[str], Dict, str]:
        """获取频道的所有播放列表"""
        api_url = "https://www.googleapis.com/youtube/v3/playlists"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {
                "part": "snippet",
                "channelId": channel_id,
                "maxResults": 50,
                "pageToken": "paginated"
            },
            "authentication": "Required (API Key)",
            "rate_limit": "10,000 quota units per day",
            "documentation": "https://developers.google.com/youtube/v3/docs/playlists/list"
        }

        playlists = []
        page_token = None

        try:
            while len(playlists) < max_playlists:
                params = {
                    "part": "snippet",
                    "channelId": channel_id,
                    "maxResults": 50,
                    "key": api_key
                }
                if page_token:
                    params["pageToken"] = page_token

                response = requests.get(api_url, params=params, timeout=10)
                if response.status_code != 200:
                    break

                data = response.json()
                items = data.get('items', [])
                if not items:
                    break

                playlists.extend([
                    f"{item['snippet']['title']}"
                    for item in items
                ])

                page_token = data.get('nextPageToken')
                if not page_token:
                    break

            question = f"列出YouTube频道 {channel_id} 的所有播放列表"
            return playlists[:max_playlists], api_info, question
        except Exception as e:
            print(f"  ✗ YouTube Playlists API错误 ({channel_id}): {e}")

        return [], api_info, ""

    # 实现抽象方法
    def fetch(self, **kwargs) -> Tuple[List[str], Dict, str]:
        channel_id = kwargs.get('channel_id')
        api_key = kwargs.get('api_key')
        if channel_id and api_key:
            return self.fetch_videos(channel_id, api_key)
        return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        return f"youtube_{kwargs.get('channel_id', 'unknown')}_videos"

    def get_metadata(self, **kwargs) -> Dict:
        return {"channel_id": kwargs.get('channel_id', ''), "platform": "YouTube"}
