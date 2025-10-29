"""Spotify API Fetcher - 精简版，完全符合Enumerate All原则"""

import requests
import os
from typing import List, Dict, Tuple
from ..base import BaseFetcher


class SpotifyFetcher(BaseFetcher):
    """Spotify API获取器 - 真正的全量枚举，无截断"""

    def __init__(self):
        self.access_token = None
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    def _get_token(self, client_id: str = None, client_secret: str = None):
        """获取Spotify访问令牌"""
        client_id = client_id or self.client_id
        client_secret = client_secret or self.client_secret

        if not client_id or not client_secret:
            raise ValueError("需要SPOTIFY_CLIENT_ID和SPOTIFY_CLIENT_SECRET")

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"},
            timeout=10
        )
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
        else:
            raise Exception(f"认证失败: {response.status_code}")

    def _ensure_token(self, token: str = None):
        """确保有可用的访问令牌"""
        if token:
            self.access_token = token
        if not self.access_token:
            self._get_token()

    def fetch_albums(self, artist_id: str, token: str = None) -> Tuple[List[Dict], Dict, str]:
        """获取艺术家的所有专辑（带完整metadata）

        返回完整的专辑对象列表，包含所有元数据：
        - id, name, release_date, album_type
        - artists (list), total_tracks
        - external_urls, etc.
        """
        self._ensure_token(token)

        api_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"limit": 50, "offset": "paginated", "include_groups": "album,single"},
            "authentication": "Required (OAuth 2.0)",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums"
        }

        albums = []
        offset = 0
        headers = {"Authorization": f"Bearer {self.access_token}"}

        while True:
            params = {"limit": 50, "offset": offset, "include_groups": "album,single"}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)

            if response.status_code != 200:
                break

            data = response.json()
            items = data.get('items', [])

            if not items:
                break

            albums.extend(items)

            # Spotify API的真正枚举终止条件
            if len(items) < 50:  # 最后一页
                break

            offset += 50

        question = f"列出Spotify艺术家ID {artist_id} 的所有专辑和单曲"
        return albums, api_info, question

    def fetch_tracks(self, album_id: str, token: str = None) -> Tuple[List[Dict], Dict, str]:
        """获取专辑的所有曲目（带完整metadata）

        返回完整的曲目对象列表，包含所有元数据：
        - id, name, track_number, duration_ms
        - explicit, artists
        - preview_url, external_urls, etc.
        """
        self._ensure_token(token)

        api_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"limit": 50, "offset": "paginated"},
            "authentication": "Required (OAuth 2.0)",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-an-albums-tracks"
        }

        tracks = []
        offset = 0
        headers = {"Authorization": f"Bearer {self.access_token}"}

        while True:
            params = {"limit": 50, "offset": offset}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)

            if response.status_code != 200:
                break

            data = response.json()
            items = data.get('items', [])

            if not items:
                break

            tracks.extend(items)

            if len(items) < 50:
                break

            offset += 50

        question = f"列出Spotify专辑ID {album_id} 的所有曲目"
        return tracks, api_info, question

    # ============================================
    # 高级过滤方法 - 基于metadata的内存过滤
    # ============================================

    def filter_collaboration_albums(self, albums: List[Dict]) -> List[Dict]:
        """筛选合作专辑（有多个艺术家）"""
        return [album for album in albums if len(album.get('artists', [])) > 1]

    def filter_albums_by_year(self, albums: List[Dict], year_start: int = None, year_end: int = None) -> List[Dict]:
        """按发行年份筛选专辑"""
        filtered = []
        for album in albums:
            release_date = album.get('release_date', '')
            if not release_date:
                continue

            year = int(release_date.split('-')[0])

            if year_start and year < year_start:
                continue
            if year_end and year > year_end:
                continue

            filtered.append(album)

        return filtered

    def filter_albums_by_type(self, albums: List[Dict], album_type: str) -> List[Dict]:
        """按专辑类型筛选（album/single/compilation）"""
        return [album for album in albums if album.get('album_type') == album_type]

    def filter_tracks_by_duration(self, tracks: List[Dict], min_ms: int = None, max_ms: int = None) -> List[Dict]:
        """按时长筛选曲目（毫秒）"""
        filtered = []
        for track in tracks:
            duration = track.get('duration_ms', 0)

            if min_ms and duration < min_ms:
                continue
            if max_ms and duration > max_ms:
                continue

            filtered.append(track)

        return filtered

    # ============================================
    # 格式化输出方法
    # ============================================

    @staticmethod
    def format_album(album: Dict) -> str:
        """格式化专辑信息为字符串"""
        artists = ', '.join([a['name'] for a in album.get('artists', [])])
        return f"{album['name']} ({album['release_date']}) - {artists}"

    @staticmethod
    def format_track(track: Dict) -> str:
        """格式化曲目信息为字符串"""
        duration_min = track.get('duration_ms', 0) // 60000
        duration_sec = (track.get('duration_ms', 0) % 60000) // 1000
        return f"{track['track_number']}. {track['name']} ({duration_min}:{duration_sec:02d})"

    # ============================================
    # 实现抽象方法
    # ============================================

    def fetch(self, **kwargs) -> Tuple[List, Dict, str]:
        artist_id = kwargs.get('artist_id')
        if artist_id:
            albums, api_info, question = self.fetch_albums(artist_id, kwargs.get('token'))
            # 转换为字符串格式以兼容旧接口
            albums_str = [self.format_album(a) for a in albums]
            return albums_str, api_info, question
        return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        return f"spotify_{kwargs.get('artist_id', 'unknown')}_albums"

    def get_metadata(self, **kwargs) -> Dict:
        return {"artist_id": kwargs.get('artist_id', ''), "platform": "Spotify"}
