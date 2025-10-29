"""The Movie Database (TMDb) API Fetcher - 精简版，完全符合Enumerate All原则"""

import requests
import os
from typing import List, Dict, Tuple
from ..base import BaseFetcher


class TMDbFetcher(BaseFetcher):
    """TMDb API获取器 - 真正的全量枚举，无截断"""

    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')

    def _ensure_api_key(self, api_key: str = None) -> str:
        """确保有可用的API密钥"""
        api_key = api_key or self.api_key
        if not api_key:
            raise ValueError("需要TMDB_API_KEY")
        return api_key

    def fetch_person_credits(self, person_id: int, api_key: str = None) -> Tuple[Dict, Dict, str]:
        """获取演员/导演的所有作品（带完整metadata）"""
        api_key = self._ensure_api_key(api_key)
        api_url = f"https://api.themoviedb.org/3/person/{person_id}/combined_credits"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"api_key": "***", "language": "zh-CN"},
            "authentication": "Required (API Key)",
            "documentation": "https://developers.themoviedb.org/3/people/get-person-combined-credits"
        }

        params = {"api_key": api_key, "language": "zh-CN"}
        response = requests.get(api_url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            question = f"列出TMDb人物ID {person_id} 的所有影视作品"
            return data, api_info, question

        return {}, api_info, ""

    def fetch_tv_seasons(self, tv_id: int, api_key: str = None) -> Tuple[List[Dict], Dict, str]:
        """获取电视剧的所有季（带完整metadata）"""
        api_key = self._ensure_api_key(api_key)
        api_url = f"https://api.themoviedb.org/3/tv/{tv_id}"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"api_key": "***", "language": "zh-CN"},
            "authentication": "Required (API Key)",
            "documentation": "https://developers.themoviedb.org/3/tv/get-tv-details"
        }

        params = {"api_key": api_key, "language": "zh-CN"}
        response = requests.get(api_url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            seasons = data.get('seasons', [])
            question = f"列出TMDb电视剧ID {tv_id} 的所有季"
            return seasons, api_info, question

        return [], api_info, ""

    def fetch_season_episodes(self, tv_id: int, season_number: int, api_key: str = None) -> Tuple[List[Dict], Dict, str]:
        """获取电视剧指定季的所有剧集（带完整metadata）"""
        api_key = self._ensure_api_key(api_key)
        api_url = f"https://api.themoviedb.org/3/tv/{tv_id}/season/{season_number}"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"api_key": "***", "language": "zh-CN"},
            "authentication": "Required (API Key)",
            "documentation": "https://developers.themoviedb.org/3/tv-seasons/get-tv-season-details"
        }

        params = {"api_key": api_key, "language": "zh-CN"}
        response = requests.get(api_url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            episodes = data.get('episodes', [])
            question = f"列出TMDb电视剧ID {tv_id} 第 {season_number} 季的所有剧集"
            return episodes, api_info, question

        return [], api_info, ""

    def fetch_movie_collection(self, collection_id: int, api_key: str = None) -> Tuple[List[Dict], Dict, str]:
        """获取电影系列的所有电影（带完整metadata）"""
        api_key = self._ensure_api_key(api_key)
        api_url = f"https://api.themoviedb.org/3/collection/{collection_id}"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"api_key": "***", "language": "zh-CN"},
            "authentication": "Required (API Key)",
            "documentation": "https://developers.themoviedb.org/3/collections/get-collection-details"
        }

        params = {"api_key": api_key, "language": "zh-CN"}
        response = requests.get(api_url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            parts = data.get('parts', [])
            # 按发行日期排序
            movies = sorted(parts, key=lambda x: x.get('release_date', ''))
            question = f"列出TMDb电影系列ID {collection_id} 的所有电影"
            return movies, api_info, question

        return [], api_info, ""

    # ============================================
    # 高级过滤方法 - 基于metadata的内存过滤
    # ============================================

    def filter_person_credits_by_role(self, credits_data: Dict, role_type: str) -> List[Dict]:
        """按角色类型筛选作品 (actor/director/producer/writer)"""
        if role_type.lower() == 'actor':
            return credits_data.get('cast', [])

        crew = credits_data.get('crew', [])
        filtered = []
        for item in crew:
            job = item.get('job', '').lower()
            department = item.get('department', '').lower()

            if role_type.lower() == 'director' and 'director' in job:
                filtered.append(item)
            elif role_type.lower() == 'producer' and ('producer' in job or 'producer' in department):
                filtered.append(item)
            elif role_type.lower() == 'writer' and ('writer' in job or 'writing' in department):
                filtered.append(item)

        return filtered

    def filter_person_credits_by_multiple_roles(
        self,
        person_id: int,
        primary_role: str,
        secondary_role: str,
        api_key: str = None
    ) -> Tuple[List[Dict], Dict, str]:
        """筛选同时满足两个角色的作品"""
        credits_data, api_info, _ = self.fetch_person_credits(person_id, api_key)

        primary_items = self.filter_person_credits_by_role(credits_data, primary_role)
        secondary_items = self.filter_person_credits_by_role(credits_data, secondary_role)

        secondary_map = {
            item.get('id'): item
            for item in secondary_items
            if item.get('id') is not None
        }

        combined = []
        for primary_item in primary_items:
            work_id = primary_item.get('id')
            if work_id is None or work_id not in secondary_map:
                continue

            secondary_item = secondary_map[work_id]
            title = (
                primary_item.get('title')
                or primary_item.get('name')
                or secondary_item.get('title')
                or secondary_item.get('name')
            )

            combined.append({
                "id": work_id,
                "title": title,
                "media_type": primary_item.get('media_type') or secondary_item.get('media_type'),
                "primary_role": primary_role,
                "secondary_role": secondary_role,
                "primary_metadata": primary_item,
                "secondary_metadata": secondary_item
            })

        question = f"列出TMDb人物ID {person_id} 同时担任 {primary_role} 和 {secondary_role} 的所有作品"

        return combined, api_info, question

    def filter_person_by_multiple_roles(
        self,
        person_id: int,
        primary_role: str,
        secondary_role: str,
        api_key: str = None
    ) -> Tuple[List[Dict], Dict, str]:
        """兼容旧接口的别名"""
        return self.filter_person_credits_by_multiple_roles(
            person_id,
            primary_role,
            secondary_role,
            api_key=api_key
        )

    def filter_person_credits_by_genre(
        self,
        person_id: int,
        genre,
        api_key: str = None
    ) -> Tuple[List[Dict], Dict, str]:
        """按类型筛选作品，支持类型ID或名称"""
        credits_data, api_info, _ = self.fetch_person_credits(person_id, api_key)

        if isinstance(genre, str):
            target = genre.strip().lower()
            genre_id = None
            genre_name = None
            for gid, name in TMDB_GENRES.items():
                if name.lower() == target:
                    genre_id = gid
                    genre_name = name
                    break
            if genre_id is None:
                for gid, name in TMDB_GENRES_EN.items():
                    if name.lower() == target:
                        genre_id = gid
                        genre_name = name
                        break
            if genre_id is None:
                raise ValueError(f"未知的类型名称: {genre}")
        else:
            genre_id = int(genre)
            genre_name = TMDB_GENRES.get(genre_id, str(genre_id))

        cast = credits_data.get('cast', [])
        crew = credits_data.get('crew', [])
        all_works = cast + crew

        filtered = []
        seen_ids = set()

        for work in all_works:
            work_id = work.get('id')
            if work_id in seen_ids:
                continue

            genre_ids = work.get('genre_ids', [])
            if genre_id in genre_ids:
                seen_ids.add(work_id)
                filtered.append(work)

        question = f"列出TMDb人物ID {person_id} 所有类型为 {genre_name} 的作品"

        return filtered, api_info, question

    def filter_episodes_with_guest_stars(
        self,
        tv_id: int,
        season_number: int,
        api_key: str = None
    ) -> Tuple[List[Dict], Dict, str]:
        """筛选指定电视剧某季中有客串明星的剧集"""
        episodes, api_info, _ = self.fetch_season_episodes(tv_id, season_number, api_key)
        filtered = [ep for ep in episodes if ep.get('guest_stars')]
        question = f"列出TMDb电视剧ID {tv_id} 第 {season_number} 季所有有客串明星的剧集"
        return filtered, api_info, question

    # ============================================
    # 格式化输出方法
    # ============================================

    @staticmethod
    def format_credit(credit: Dict, role: str = None) -> str:
        """格式化作品信息为字符串"""
        title = credit.get('title') or credit.get('name', 'Unknown')
        year = (credit.get('release_date') or credit.get('first_air_date', ''))[:4]
        media_type = credit.get('media_type', 'unknown')

        if not role:
            # 自动判断角色
            if 'character' in credit:
                role = f"饰演 {credit['character']}"
            elif 'job' in credit:
                role = credit['job']
            else:
                role = "未知"

        return f"[{role}] {title} ({year}) [{media_type}]"

    @staticmethod
    def format_season(season: Dict) -> str:
        """格式化季信息为字符串"""
        name = season.get('name', 'Unknown')
        ep_count = season.get('episode_count', 0)
        air_date = season.get('air_date', 'TBA')
        return f"{name} ({ep_count} episodes) - {air_date}"

    @staticmethod
    def format_episode(episode: Dict) -> str:
        """格式化剧集信息为字符串"""
        season = episode.get('season_number', 0)
        ep_num = episode.get('episode_number', 0)
        name = episode.get('name', 'Unknown')
        air_date = episode.get('air_date', 'TBA')
        return f"S{season:02d}E{ep_num:02d}: {name} - {air_date}"

    @staticmethod
    def format_movie(movie: Dict) -> str:
        """格式化电影信息为字符串"""
        title = movie.get('title', 'Unknown')
        year = movie.get('release_date', 'TBA')[:4]
        return f"{title} ({year})"

    # ============================================
    # 实现抽象方法
    # ============================================

    def fetch(self, **kwargs) -> Tuple[List, Dict, str]:
        api_key = kwargs.get('api_key')

        if kwargs.get('person_id'):
            credits_data, api_info, question = self.fetch_person_credits(kwargs['person_id'], api_key)
            # 转换为字符串格式以兼容旧接口
            cast = credits_data.get('cast', [])
            crew = credits_data.get('crew', [])
            all_credits = []
            for item in cast:
                all_credits.append(self.format_credit(item))
            for item in crew:
                all_credits.append(self.format_credit(item))
            return all_credits, api_info, question

        elif kwargs.get('tv_id'):
            seasons, api_info, question = self.fetch_tv_seasons(kwargs['tv_id'], api_key)
            seasons_str = [self.format_season(s) for s in seasons]
            return seasons_str, api_info, question

        elif kwargs.get('collection_id'):
            movies, api_info, question = self.fetch_movie_collection(kwargs['collection_id'], api_key)
            movies_str = [self.format_movie(m) for m in movies]
            return movies_str, api_info, question

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

# TMDb类型映射（用于高级查询）
TMDB_GENRES = {
    28: "动作", 12: "冒险", 16: "动画", 35: "喜剧", 80: "犯罪",
    99: "纪录", 18: "剧情", 10751: "家庭", 14: "奇幻", 36: "历史",
    27: "恐怖", 10402: "音乐", 9648: "悬疑", 10749: "爱情", 878: "科幻",
    10770: "电视电影", 53: "惊悚", 10752: "战争", 37: "西部"
}

# 兼容英文类型名称
TMDB_GENRES_EN = {
    28: "action", 12: "adventure", 16: "animation", 35: "comedy", 80: "crime",
    99: "documentary", 18: "drama", 10751: "family", 14: "fantasy", 36: "history",
    27: "horror", 10402: "music", 9648: "mystery", 10749: "romance", 878: "science fiction",
    10770: "tv movie", 53: "thriller", 10752: "war", 37: "western"
}
