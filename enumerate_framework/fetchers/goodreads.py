"""Open Library API Fetcher (Goodreads alternative)"""

import requests
from typing import List, Dict, Tuple
from .base import BaseFetcher


class OpenLibraryFetcher(BaseFetcher):
    """Open Library图书数据获取器 (Goodreads的开放替代品)"""

    def fetch_author_works(self, author_key: str, max_works: int = 1000) -> Tuple[List[str], Dict, str]:
        """获取作者的所有作品"""
        api_url = f"https://openlibrary.org/authors/{author_key}/works.json"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"limit": 50, "offset": "paginated"},
            "authentication": "None",
            "rate_limit": "No official limit (be respectful)",
            "documentation": "https://openlibrary.org/dev/docs/api/books"
        }

        works = []
        offset = 0
        limit = 50

        try:
            while offset < max_works:
                params = {"limit": limit, "offset": offset}
                response = requests.get(api_url, params=params, timeout=10)

                if response.status_code != 200:
                    break

                data = response.json()
                entries = data.get('entries', [])
                if not entries:
                    break

                for work in entries:
                    title = work.get('title', 'Unknown')
                    first_publish_year = work.get('first_publish_year', 'Unknown')
                    works.append(f"{title} ({first_publish_year})")

                if len(entries) < limit:
                    break

                offset += limit

            question = f"列出Open Library作者 {author_key} 的所有作品"
            return works[:max_works], api_info, question

        except Exception as e:
            print(f"  ✗ Open Library API错误 ({author_key}): {e}")

        return [], api_info, ""

    def fetch_book_editions(self, work_id: str, max_editions: int = 500) -> Tuple[List[str], Dict, str]:
        """获取一本书的所有版本"""
        api_url = f"https://openlibrary.org/works/{work_id}/editions.json"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"limit": 50, "offset": "paginated"},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://openlibrary.org/dev/docs/api/books"
        }

        editions = []
        offset = 0
        limit = 50

        try:
            while offset < max_editions:
                params = {"limit": limit, "offset": offset}
                response = requests.get(api_url, params=params, timeout=10)

                if response.status_code != 200:
                    break

                data = response.json()
                entries = data.get('entries', [])
                if not entries:
                    break

                for edition in entries:
                    title = edition.get('title', 'Unknown')
                    publish_date = edition.get('publish_date', 'Unknown')
                    publishers = ', '.join(edition.get('publishers', ['Unknown']))
                    editions.append(f"{title} - {publishers} ({publish_date})")

                if len(entries) < limit:
                    break

                offset += limit

            question = f"列出Open Library作品 {work_id} 的所有版本"
            return editions[:max_editions], api_info, question

        except Exception as e:
            print(f"  ✗ Open Library API错误 ({work_id}): {e}")

        return [], api_info, ""

    # 实现抽象方法
    def fetch(self, **kwargs) -> Tuple[List[str], Dict, str]:
        if kwargs.get('author_key'):
            return self.fetch_author_works(kwargs['author_key'])
        elif kwargs.get('work_id'):
            return self.fetch_book_editions(kwargs['work_id'])
        return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        if kwargs.get('author_key'):
            return f"openlibrary_author_{kwargs['author_key']}"
        elif kwargs.get('work_id'):
            return f"openlibrary_work_{kwargs['work_id']}"
        return "openlibrary_unknown"

    def get_metadata(self, **kwargs) -> Dict:
        return {
            "author_key": kwargs.get('author_key'),
            "work_id": kwargs.get('work_id'),
            "platform": "Open Library"
        }
