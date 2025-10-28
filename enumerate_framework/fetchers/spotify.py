"""Spotify API Fetcher"""

import requests
import os
from typing import List, Dict, Tuple
from .base import BaseFetcher


class SpotifyFetcher(BaseFetcher):
    """Spotify艺术家专辑获取器"""

    def __init__(self):
        self.access_token = None
        # 尝试从环境变量获取凭据
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    def _get_token(self, client_id: str = None, client_secret: str = None):
        """获取Spotify访问令牌"""
        # 优先使用传入的参数，否则使用环境变量
        client_id = client_id or self.client_id
        client_secret = client_secret or self.client_secret

        if not client_id or not client_secret:
            raise ValueError("需要SPOTIFY_CLIENT_ID和SPOTIFY_CLIENT_SECRET。"
                           "请在.env文件中设置或作为参数传入。")

        auth_url = "https://accounts.spotify.com/api/token"
        auth_data = {"grant_type": "client_credentials"}
        try:
            response = requests.post(
                auth_url,
                auth=(client_id, client_secret),
                data=auth_data,
                timeout=10
            )
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
            else:
                raise Exception(f"认证失败: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Spotify Token错误: {e}")
            raise

    def fetch_albums(self, artist_id: str, token: str = None, max_albums: int = 1000) -> Tuple[List[str], Dict, str]:
        """获取艺术家的所有专辑"""
        if token:
            self.access_token = token

        if not self.access_token:
            # 尝试自动获取token
            try:
                self._get_token()
            except Exception:
                print("  ✗ 无法获取Spotify访问令牌。请配置SPOTIFY_CLIENT_ID和SPOTIFY_CLIENT_SECRET")
                return [], {}, ""

        api_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"limit": 50, "offset": "paginated", "include_groups": "album,single"},
            "authentication": "Required (OAuth 2.0)",
            "rate_limit": "Varies by endpoint",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums"
        }

        albums = []
        offset = 0
        limit = 50

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            while offset < max_albums:
                params = {
                    "limit": limit,
                    "offset": offset,
                    "include_groups": "album,single"
                }
                response = requests.get(api_url, headers=headers, params=params, timeout=10)
                if response.status_code != 200:
                    break

                data = response.json()
                items = data.get('items', [])
                if not items:
                    break

                albums.extend([f"{album['name']} ({album['release_date']})" for album in items])

                if len(items) < limit:
                    break

                offset += limit

            question = f"列出Spotify艺术家ID {artist_id} 的所有专辑和单曲"
            return albums[:max_albums], api_info, question
        except Exception as e:
            print(f"  ✗ Spotify Albums API错误 ({artist_id}): {e}")

        return [], api_info, ""

    def fetch_tracks(self, album_id: str, token: str = None) -> Tuple[List[str], Dict, str]:
        """获取专辑的所有曲目"""
        if token:
            self.access_token = token

        if not self.access_token:
            print("  ✗ 需要Spotify访问令牌")
            return [], {}, ""

        api_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"limit": 50, "offset": "paginated"},
            "authentication": "Required (OAuth 2.0)",
            "rate_limit": "Varies by endpoint",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-an-albums-tracks"
        }

        tracks = []
        offset = 0
        limit = 50

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            while True:
                params = {"limit": limit, "offset": offset}
                response = requests.get(api_url, headers=headers, params=params, timeout=10)
                if response.status_code != 200:
                    break

                data = response.json()
                items = data.get('items', [])
                if not items:
                    break

                tracks.extend([f"{track['track_number']}. {track['name']}" for track in items])

                if len(items) < limit:
                    break

                offset += limit

            question = f"列出Spotify专辑ID {album_id} 的所有曲目"
            return tracks, api_info, question
        except Exception as e:
            print(f"  ✗ Spotify Tracks API错误 ({album_id}): {e}")

        return [], api_info, ""

    # 实现抽象方法
    def fetch(self, **kwargs) -> Tuple[List[str], Dict, str]:
        artist_id = kwargs.get('artist_id')
        token = kwargs.get('token')
        if artist_id:
            return self.fetch_albums(artist_id, token)
        return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        return f"spotify_{kwargs.get('artist_id', 'unknown')}_albums"

    def get_metadata(self, **kwargs) -> Dict:
        return {"artist_id": kwargs.get('artist_id', ''), "platform": "Spotify"}
