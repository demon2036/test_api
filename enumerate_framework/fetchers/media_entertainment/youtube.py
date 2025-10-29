"""YouTube Data API Fetcher - 精简版，完全符合Enumerate All原则"""

import requests
import os
import re
from typing import List, Dict, Tuple
from ..base import BaseFetcher


class YouTubeFetcher(BaseFetcher):
    """YouTube API获取器 - 真正的全量枚举，无截断"""

    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')

    def _ensure_api_key(self, api_key: str = None) -> str:
        """确保有可用的API密钥"""
        api_key = api_key or self.api_key
        if not api_key:
            raise ValueError("需要YOUTUBE_API_KEY")
        return api_key

    def _parse_duration(self, duration_str: str) -> int:
        """将YouTube的ISO 8601格式时长转换为秒数"""
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        if not match:
            return 0
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds

    def fetch_videos(self, channel_id: str, api_key: str = None) -> Tuple[List[Dict], Dict, str]:
        """获取频道的所有视频（带完整metadata）- 使用uploads playlist避免search API的500结果限制"""
        api_key = self._ensure_api_key(api_key)

        # 第一步：获取频道的uploads playlist ID 和频道名称
        channel_url = "https://www.googleapis.com/youtube/v3/channels"
        channel_params = {
            "part": "contentDetails,snippet",  # 添加 snippet 以获取频道名称
            "id": channel_id,
            "key": api_key
        }
        channel_response = requests.get(channel_url, params=channel_params, timeout=10)
        if channel_response.status_code != 200:
            raise Exception(f"Failed to get channel info: {channel_response.status_code}")

        channel_data = channel_response.json()
        if not channel_data.get('items'):
            raise Exception(f"Channel not found: {channel_id}")

        # 获取频道名称和uploads playlist ID
        channel_name = channel_data['items'][0]['snippet']['title']
        uploads_playlist_id = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # 第二步：从uploads playlist获取所有视频ID（无500限制）
        playlist_url = "https://www.googleapis.com/youtube/v3/playlistItems"
        video_ids = []
        page_token = None

        while True:
            params = {
                "part": "contentDetails",
                "playlistId": uploads_playlist_id,
                "maxResults": 50,
                "key": api_key
            }
            if page_token:
                params["pageToken"] = page_token

            response = requests.get(playlist_url, params=params, timeout=10)
            if response.status_code != 200:
                break

            data = response.json()
            items = data.get('items', [])
            if not items:
                break

            video_ids.extend([item['contentDetails']['videoId'] for item in items])

            page_token = data.get('nextPageToken')
            if not page_token:
                break

        # 第三步：批量获取视频详细信息
        detailed_videos = []
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            details_url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "snippet,contentDetails,statistics",
                "id": ",".join(batch_ids),
                "key": api_key
            }
            response = requests.get(details_url, params=params, timeout=10)
            if response.status_code == 200:
                detailed_videos.extend(response.json().get('items', []))

        # 为每个视频添加频道信息
        for video in detailed_videos:
            video['_channel_id'] = channel_id
            video['_channel_name'] = channel_name

        api_info = {
            "api_endpoint": playlist_url,
            "method": "GET",
            "parameters": {"part": "contentDetails", "playlistId": "uploads", "pageToken": "paginated"},
            "authentication": "Required (API Key)",
            "documentation": "https://developers.google.com/youtube/v3/docs/playlistItems/list",
            "note": "使用uploads playlist避免search API的500结果限制"
        }

        question = f"列出YouTube频道 {channel_name} ({channel_id}) 的所有视频"
        return detailed_videos, api_info, question

    def fetch_playlists(self, channel_id: str, api_key: str = None) -> Tuple[List[Dict], Dict, str]:
        """获取频道的所有播放列表（带完整metadata）"""
        api_key = self._ensure_api_key(api_key)
        api_url = "https://www.googleapis.com/youtube/v3/playlists"

        playlists = []
        page_token = None

        while True:
            params = {
                "part": "snippet,contentDetails",
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

            playlists.extend(items)

            page_token = data.get('nextPageToken')
            if not page_token:
                break

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"part": "snippet,contentDetails", "pageToken": "paginated"},
            "authentication": "Required (API Key)",
            "documentation": "https://developers.google.com/youtube/v3/docs/playlists/list"
        }

        question = f"列出YouTube频道 {channel_id} 的所有播放列表"
        return playlists, api_info, question

    # ============================================
    # 高级过滤方法 - 基于metadata的内存过滤
    # ============================================

    def _get_channel_display_name(self, video: Dict) -> str:
        """从视频对象中获取频道显示名称"""
        channel_name = video.get('_channel_name', '')
        channel_id = video.get('_channel_id', '')
        if channel_name:
            return f"{channel_name} ({channel_id})"
        return channel_id

    def add_video_metadata(self, video: Dict) -> Dict:
        """为视频添加解析后的元信息（时长、观看次数等）"""
        enhanced_video = video.copy()

        # 添加解析后的时长信息
        duration_str = video.get('contentDetails', {}).get('duration', '')
        duration_seconds = self._parse_duration(duration_str)
        enhanced_video['duration_seconds'] = duration_seconds
        enhanced_video['duration_minutes'] = round(duration_seconds / 60, 2)

        # 添加格式化的观看次数
        view_count = int(video.get('statistics', {}).get('viewCount', 0))
        enhanced_video['view_count'] = view_count

        # 添加视频URL
        enhanced_video['url'] = f"https://www.youtube.com/watch?v={video['id']}"

        return enhanced_video

    def filter_videos_by_duration(self, videos: List[Dict], min_seconds: int = None, max_seconds: int = None) -> List[Dict]:
        """按时长筛选视频，并在返回的视频中添加解析后的时长信息"""
        filtered = []
        for video in videos:
            # 添加元信息
            enhanced_video = self.add_video_metadata(video)
            duration_seconds = enhanced_video['duration_seconds']

            if min_seconds and duration_seconds < min_seconds:
                continue
            if max_seconds and duration_seconds > max_seconds:
                continue

            filtered.append(enhanced_video)

        return filtered

    def filter_videos_by_views(self, videos: List[Dict], min_views: int = None, max_views: int = None) -> List[Dict]:
        """按观看次数筛选视频，并在返回的视频中添加元信息"""
        filtered = []
        for video in videos:
            # 添加元信息
            enhanced_video = self.add_video_metadata(video)
            view_count = enhanced_video['view_count']

            if min_views and view_count < min_views:
                continue
            if max_views and view_count > max_views:
                continue

            filtered.append(enhanced_video)

        return filtered

    def get_most_viewed_video(self, videos: List[Dict]) -> Dict:
        """找出观看次数最多的视频，返回增强的元信息"""
        if not videos:
            return {}
        most_viewed = max(videos, key=lambda v: int(v.get('statistics', {}).get('viewCount', 0)))
        return self.add_video_metadata(most_viewed)

    # ============================================
    # 格式化输出方法
    # ============================================

    @staticmethod
    def format_video(video: Dict) -> str:
        """格式化视频信息为字符串"""
        title = video['snippet']['title']
        date = video['snippet']['publishedAt'][:10]
        view_count = int(video.get('statistics', {}).get('viewCount', 0))
        return f"{title} ({date}) - {view_count:,} 次观看"

    @staticmethod
    def format_playlist(playlist: Dict) -> str:
        """格式化播放列表信息为字符串"""
        title = playlist['snippet']['title']
        item_count = playlist.get('contentDetails', {}).get('itemCount', 0)
        return f"{title} ({item_count} 个视频)"

    # ============================================
    # 实现抽象方法
    # ============================================

    def fetch(self, **kwargs) -> Tuple[List, Dict, str]:
        channel_id = kwargs.get('channel_id')
        api_key = kwargs.get('api_key')
        if channel_id:
            videos, api_info, question = self.fetch_videos(channel_id, api_key)
            # 转换为字符串格式以兼容旧接口
            videos_str = [self.format_video(v) for v in videos]
            return videos_str, api_info, question
        return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        return f"youtube_{kwargs.get('channel_id', 'unknown')}_videos"

    def get_metadata(self, **kwargs) -> Dict:
        return {"channel_id": kwargs.get('channel_id', ''), "platform": "YouTube"}
