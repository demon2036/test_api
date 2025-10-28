"""IMDb API Fetcher (using OMDb API)"""

import requests
from typing import List, Dict, Tuple
from .base import BaseFetcher


class IMDbFetcher(BaseFetcher):
    """IMDb电影/剧集信息获取器 (via OMDb API)"""

    def fetch_person_filmography(self, person_name: str, api_key: str) -> Tuple[List[str], Dict, str]:
        """
        Note: OMDb API doesn't support filmography listings directly.
        This is a simplified example. For complete filmography, you would need:
        1. IMDb's official API (requires special access)
        2. Web scraping (not recommended)
        3. Alternative APIs like TMDb
        """
        api_url = "http://www.omdbapi.com/"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"s": person_name, "type": "movie"},
            "authentication": "Required (API Key)",
            "rate_limit": "1,000 requests/day (free tier)",
            "documentation": "http://www.omdbapi.com/"
        }

        movies = []

        try:
            params = {
                "s": person_name,
                "apikey": api_key
            }
            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'True':
                    results = data.get('Search', [])
                    movies = [f"{item['Title']} ({item['Year']})" for item in results]

            question = f"搜索与 {person_name} 相关的电影"
            return movies, api_info, question
        except Exception as e:
            print(f"  ✗ OMDb API错误 ({person_name}): {e}")

        return [], api_info, ""

    # 实现抽象方法
    def fetch(self, **kwargs) -> Tuple[List[str], Dict, str]:
        person_name = kwargs.get('person_name')
        api_key = kwargs.get('api_key')
        if person_name and api_key:
            return self.fetch_person_filmography(person_name, api_key)
        return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        return f"imdb_{kwargs.get('person_name', 'unknown').replace(' ', '_')}"

    def get_metadata(self, **kwargs) -> Dict:
        return {"person_name": kwargs.get('person_name', ''), "platform": "IMDb/OMDb"}
