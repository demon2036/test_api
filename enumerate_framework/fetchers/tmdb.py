"""The Movie Database (TMDb) API Fetcher"""

import requests
import os
from typing import List, Dict, Tuple
from .base import BaseFetcher


class TMDbFetcher(BaseFetcher):
    """TMDb电影/电视剧数据获取器"""

    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')

    def fetch_person_credits(self, person_id: int, api_key: str = None) -> Tuple[List[str], Dict, str]:
        """获取演员/导演的所有作品"""
        # 使用传入的api_key或环境变量
        api_key = api_key or self.api_key
        if not api_key:
            print("  ✗ 需要TMDb API Key。请在.env中设置TMDB_API_KEY或作为参数传入")
            return [], {}, ""

        api_url = f"https://api.themoviedb.org/3/person/{person_id}/combined_credits"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"api_key": api_key, "language": "zh-CN"},
            "authentication": "Required (API Key)",
            "rate_limit": "40 requests every 10 seconds",
            "documentation": "https://developers.themoviedb.org/3/people/get-person-combined-credits"
        }

        try:
            params = {"api_key": api_key, "language": "zh-CN"}
            response = requests.get(api_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                cast = data.get('cast', [])
                crew = data.get('crew', [])

                all_credits = []
                # 演员作品
                for item in cast:
                    title = item.get('title') or item.get('name', 'Unknown')
                    year = (item.get('release_date') or item.get('first_air_date', ''))[:4]
                    media_type = item.get('media_type', 'unknown')
                    all_credits.append(f"[演员] {title} ({year}) [{media_type}]")

                # 幕后作品
                for item in crew:
                    title = item.get('title') or item.get('name', 'Unknown')
                    year = (item.get('release_date') or item.get('first_air_date', ''))[:4]
                    job = item.get('job', 'Unknown')
                    media_type = item.get('media_type', 'unknown')
                    all_credits.append(f"[{job}] {title} ({year}) [{media_type}]")

                question = f"列出TMDb人物ID {person_id} 的所有影视作品"
                return all_credits, api_info, question

        except Exception as e:
            print(f"  ✗ TMDb API错误 (person {person_id}): {e}")

        return [], api_info, ""

    def fetch_tv_seasons(self, tv_id: int, api_key: str) -> Tuple[List[str], Dict, str]:
        """获取电视剧的所有季"""
        api_url = f"https://api.themoviedb.org/3/tv/{tv_id}"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"api_key": api_key, "language": "zh-CN"},
            "authentication": "Required (API Key)",
            "rate_limit": "40 requests every 10 seconds",
            "documentation": "https://developers.themoviedb.org/3/tv/get-tv-details"
        }

        try:
            params = {"api_key": api_key, "language": "zh-CN"}
            response = requests.get(api_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                seasons = data.get('seasons', [])
                season_list = [
                    f"{season['name']} ({season['episode_count']} episodes) - {season['air_date'] or 'TBA'}"
                    for season in seasons
                ]

                question = f"列出TMDb电视剧ID {tv_id} 的所有季"
                return season_list, api_info, question

        except Exception as e:
            print(f"  ✗ TMDb API错误 (TV {tv_id}): {e}")

        return [], api_info, ""

    def fetch_movie_collection(self, collection_id: int, api_key: str) -> Tuple[List[str], Dict, str]:
        """获取电影系列的所有电影"""
        api_url = f"https://api.themoviedb.org/3/collection/{collection_id}"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"api_key": api_key, "language": "zh-CN"},
            "authentication": "Required (API Key)",
            "rate_limit": "40 requests every 10 seconds",
            "documentation": "https://developers.themoviedb.org/3/collections/get-collection-details"
        }

        try:
            params = {"api_key": api_key, "language": "zh-CN"}
            response = requests.get(api_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                parts = data.get('parts', [])
                movies = [
                    f"{movie['title']} ({movie.get('release_date', 'TBA')[:4]})"
                    for movie in sorted(parts, key=lambda x: x.get('release_date', ''))
                ]

                question = f"列出TMDb电影系列ID {collection_id} 的所有电影"
                return movies, api_info, question

        except Exception as e:
            print(f"  ✗ TMDb API错误 (Collection {collection_id}): {e}")

        return [], api_info, ""

    # 实现抽象方法
    def fetch(self, **kwargs) -> Tuple[List[str], Dict, str]:
        api_key = kwargs.get('api_key')
        if kwargs.get('person_id') and api_key:
            return self.fetch_person_credits(kwargs['person_id'], api_key)
        elif kwargs.get('tv_id') and api_key:
            return self.fetch_tv_seasons(kwargs['tv_id'], api_key)
        elif kwargs.get('collection_id') and api_key:
            return self.fetch_movie_collection(kwargs['collection_id'], api_key)
        return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        if kwargs.get('person_id'):
            return f"tmdb_person_{kwargs['person_id']}"
        elif kwargs.get('tv_id'):
            return f"tmdb_tv_{kwargs['tv_id']}"
        elif kwargs.get('collection_id'):
            return f"tmdb_collection_{kwargs['collection_id']}"
        return "tmdb_unknown"

    def get_metadata(self, **kwargs) -> Dict:
        return {
            "person_id": kwargs.get('person_id'),
            "tv_id": kwargs.get('tv_id'),
            "collection_id": kwargs.get('collection_id'),
            "platform": "TMDb"
        }
