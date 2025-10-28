"""Wikipedia API Fetcher"""

import requests
from typing import List, Dict, Tuple
from .base import BaseFetcher


class WikipediaFetcher(BaseFetcher):
    """Wikipedia数据获取器"""

    def fetch_category_members(self, category: str, lang: str = "en", max_members: int = 5000) -> Tuple[List[str], Dict, str]:
        """获取Wikipedia分类下的所有页面"""
        api_url = f"https://{lang}.wikipedia.org/w/api.php"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{category}",
                "cmlimit": 500,
                "cmcontinue": "paginated"
            },
            "authentication": "None",
            "rate_limit": "No strict limit (be respectful)",
            "documentation": "https://www.mediawiki.org/wiki/API:Categorymembers"
        }

        members = []
        continue_param = {}

        try:
            while len(members) < max_members:
                params = {
                    "action": "query",
                    "list": "categorymembers",
                    "cmtitle": f"Category:{category}",
                    "cmlimit": 500,
                    "format": "json"
                }
                params.update(continue_param)

                response = requests.get(api_url, params=params, timeout=10)
                if response.status_code != 200:
                    break

                data = response.json()
                items = data.get('query', {}).get('categorymembers', [])
                if not items:
                    break

                members.extend([item['title'] for item in items])

                # Check for continuation
                if 'continue' in data:
                    continue_param = data['continue']
                else:
                    break

            question = f"列出Wikipedia ({lang})分类'{category}'下的所有页面"
            return members[:max_members], api_info, question

        except Exception as e:
            print(f"  ✗ Wikipedia API错误 ({category}): {e}")

        return [], api_info, ""

    def fetch_page_revisions(self, page_title: str, lang: str = "en", max_revisions: int = 5000) -> Tuple[List[str], Dict, str]:
        """获取Wikipedia页面的所有修订版本"""
        api_url = f"https://{lang}.wikipedia.org/w/api.php"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {
                "action": "query",
                "prop": "revisions",
                "titles": page_title,
                "rvlimit": 500,
                "rvcontinue": "paginated"
            },
            "authentication": "None",
            "rate_limit": "No strict limit",
            "documentation": "https://www.mediawiki.org/wiki/API:Revisions"
        }

        revisions = []
        continue_param = {}

        try:
            while len(revisions) < max_revisions:
                params = {
                    "action": "query",
                    "prop": "revisions",
                    "titles": page_title,
                    "rvprop": "timestamp|user|comment|ids",
                    "rvlimit": 500,
                    "format": "json"
                }
                params.update(continue_param)

                response = requests.get(api_url, params=params, timeout=10)
                if response.status_code != 200:
                    break

                data = response.json()
                pages = data.get('query', {}).get('pages', {})
                if not pages:
                    break

                # Get first (and only) page
                page = list(pages.values())[0]
                revs = page.get('revisions', [])
                if not revs:
                    break

                for rev in revs:
                    timestamp = rev.get('timestamp', 'Unknown')
                    user = rev.get('user', 'Unknown')
                    comment = rev.get('comment', '')[:100]  # Truncate long comments
                    revid = rev.get('revid', '')
                    revisions.append(f"[{timestamp}] by {user}: {comment} (revid: {revid})")

                # Check for continuation
                if 'continue' in data:
                    continue_param = data['continue']
                else:
                    break

            question = f"列出Wikipedia ({lang})页面'{page_title}'的所有修订版本"
            return revisions[:max_revisions], api_info, question

        except Exception as e:
            print(f"  ✗ Wikipedia API错误 ({page_title}): {e}")

        return [], api_info, ""

    def fetch_page_links(self, page_title: str, lang: str = "en", max_links: int = 5000) -> Tuple[List[str], Dict, str]:
        """获取Wikipedia页面的所有内部链接"""
        api_url = f"https://{lang}.wikipedia.org/w/api.php"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {
                "action": "query",
                "prop": "links",
                "titles": page_title,
                "pllimit": 500,
                "plcontinue": "paginated"
            },
            "authentication": "None",
            "rate_limit": "No strict limit",
            "documentation": "https://www.mediawiki.org/wiki/API:Links"
        }

        links = []
        continue_param = {}

        try:
            while len(links) < max_links:
                params = {
                    "action": "query",
                    "prop": "links",
                    "titles": page_title,
                    "pllimit": 500,
                    "format": "json"
                }
                params.update(continue_param)

                response = requests.get(api_url, params=params, timeout=10)
                if response.status_code != 200:
                    break

                data = response.json()
                pages = data.get('query', {}).get('pages', {})
                if not pages:
                    break

                page = list(pages.values())[0]
                page_links = page.get('links', [])
                if not page_links:
                    break

                links.extend([link['title'] for link in page_links])

                if 'continue' in data:
                    continue_param = data['continue']
                else:
                    break

            question = f"列出Wikipedia ({lang})页面'{page_title}'的所有内部链接"
            return links[:max_links], api_info, question

        except Exception as e:
            print(f"  ✗ Wikipedia API错误 ({page_title}): {e}")

        return [], api_info, ""

    # 实现抽象方法
    def fetch(self, **kwargs) -> Tuple[List[str], Dict, str]:
        lang = kwargs.get('lang', 'en')
        if kwargs.get('category'):
            return self.fetch_category_members(kwargs['category'], lang)
        elif kwargs.get('page_title') and kwargs.get('type') == 'revisions':
            return self.fetch_page_revisions(kwargs['page_title'], lang)
        elif kwargs.get('page_title') and kwargs.get('type') == 'links':
            return self.fetch_page_links(kwargs['page_title'], lang)
        return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        if kwargs.get('category'):
            return f"wikipedia_{kwargs.get('lang', 'en')}_category_{kwargs['category'].replace(' ', '_')}"
        elif kwargs.get('page_title'):
            return f"wikipedia_{kwargs.get('lang', 'en')}_page_{kwargs['page_title'].replace(' ', '_')}"
        return "wikipedia_unknown"

    def get_metadata(self, **kwargs) -> Dict:
        return {
            "category": kwargs.get('category'),
            "page_title": kwargs.get('page_title'),
            "lang": kwargs.get('lang', 'en'),
            "type": kwargs.get('type'),
            "platform": "Wikipedia"
        }
