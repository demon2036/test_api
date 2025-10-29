"""Open Library API Fetcher (Goodreads alternative) - Enhanced with full metadata

⚠️ DEPRECATED (2025-10-29) ⚠️
This fetcher has been removed from the framework due to data quality issues.

Reason: The Open Library API has severe data quality problems:
- Same work appears multiple times with different work IDs for different language editions
- Translations are incorrectly created as separate works instead of editions
- Cannot accurately enumerate unique works by an author

This violates the "Enumerate All" principles:
- Precision: Cannot precisely identify unique works
- Completeness: Results include duplicates
- Determinism: Cannot guarantee correct enumeration

See GEMINI.md "Deprecated/Removed APIs" section for details.
"""

import requests
from typing import List, Dict, Tuple
from ..base import BaseFetcher


class OpenLibraryFetcher(BaseFetcher):
    """Open Library图书数据获取器 - 完整metadata支持"""

    def fetch_author_works(self, author_key: str, max_works: int = 1000) -> Tuple[List[Dict], Dict, str]:
        """获取作者的所有作品（带完整metadata）

        返回完整的作品对象列表，包含所有元数据：
        - title, key, first_publish_year
        - subjects, covers, edition_count
        - languages (需要额外API调用获取)
        """
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

                # 保存完整的work对象
                works.extend(entries)

                if len(entries) < limit:
                    break

                offset += limit

            question = f"列出Open Library作者 {author_key} 的所有作品"
            return works[:max_works], api_info, question

        except Exception as e:
            print(f"  ✗ Open Library API错误 ({author_key}): {e}")

        return [], api_info, ""

    def fetch_book_editions(self, work_id: str, max_editions: int = 500) -> Tuple[List[Dict], Dict, str]:
        """获取一本书的所有版本（带完整metadata）

        返回完整的版本对象列表，包含所有元数据：
        - title, key, publish_date, publishers
        - number_of_pages, languages
        - isbn_10, isbn_13
        """
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

                # 保存完整的edition对象
                editions.extend(entries)

                if len(entries) < limit:
                    break

                offset += limit

            question = f"列出Open Library作品 {work_id} 的所有版本"
            return editions[:max_editions], api_info, question

        except Exception as e:
            print(f"  ✗ Open Library API错误 ({work_id}): {e}")

        return [], api_info, ""

    # ============================================
    # 高级过滤方法 - 基于metadata的内存过滤
    # ============================================

    def filter_by_languages(self, works: List[Dict], min_languages: int) -> List[Dict]:
        """筛选被翻译成至少min_languages种语言的作品

        注意：需要先获取每个作品的版本数据来统计语言数量
        """
        filtered = []
        for work in works:
            work_key = work.get('key', '').replace('/works/', '')
            if not work_key:
                continue

            # 获取该作品的所有版本
            try:
                editions, _, _ = self.fetch_book_editions(work_key, max_editions=1000)

                # 统计语言种类
                languages = set()
                for edition in editions:
                    edition_langs = edition.get('languages', [])
                    for lang in edition_langs:
                        if isinstance(lang, dict):
                            lang_key = lang.get('key', '')
                            languages.add(lang_key)
                        elif isinstance(lang, str):
                            languages.add(lang)

                # 添加语言信息到work对象
                work['_language_count'] = len(languages)
                work['_languages'] = list(languages)

                if len(languages) >= min_languages:
                    filtered.append(work)

            except Exception as e:
                print(f"  警告: 无法获取作品 {work_key} 的语言信息: {e}")
                continue

        return filtered

    def find_first_edition(self, work_id: str) -> Dict:
        """找到某本书的第一版（最早出版的版本）"""
        editions, _, _ = self.fetch_book_editions(work_id, max_editions=1000)

        if not editions:
            return {}

        # 筛选有明确出版日期的版本
        editions_with_date = []
        for edition in editions:
            publish_date = edition.get('publish_date', '')
            if publish_date and publish_date != 'Unknown':
                # 尝试提取年份
                try:
                    # 可能的格式：'1954', 'January 1954', '1954-01-01'等
                    year = None
                    if publish_date.isdigit() and len(publish_date) == 4:
                        year = int(publish_date)
                    else:
                        # 尝试提取最后4个连续数字
                        import re
                        year_match = re.search(r'\b(\d{4})\b', publish_date)
                        if year_match:
                            year = int(year_match.group(1))

                    if year:
                        editions_with_date.append({
                            'edition': edition,
                            'year': year,
                            'publish_date': publish_date
                        })
                except:
                    continue

        if not editions_with_date:
            # 如果没有日期信息，返回第一个版本
            return editions[0]

        # 按年份排序，返回最早的
        editions_with_date.sort(key=lambda x: x['year'])
        return editions_with_date[0]['edition']

    def filter_by_page_count(self, works: List[Dict], min_pages: int = None, max_pages: int = None) -> List[Dict]:
        """筛选页数在指定范围内的作品

        注意：需要检查该作品的各个版本的页数
        """
        filtered = []
        for work in works:
            work_key = work.get('key', '').replace('/works/', '')
            if not work_key:
                continue

            # 获取该作品的所有版本
            try:
                editions, _, _ = self.fetch_book_editions(work_key, max_editions=1000)

                # 检查是否有任何版本符合页数要求
                has_matching_edition = False
                max_page_count = 0

                for edition in editions:
                    pages = edition.get('number_of_pages', 0)
                    if not pages:
                        continue

                    max_page_count = max(max_page_count, pages)

                    if min_pages and pages < min_pages:
                        continue
                    if max_pages and pages > max_pages:
                        continue

                    has_matching_edition = True
                    break

                if has_matching_edition:
                    work['_max_pages'] = max_page_count
                    filtered.append(work)

            except Exception as e:
                print(f"  警告: 无法获取作品 {work_key} 的页数信息: {e}")
                continue

        return filtered

    # ============================================
    # 格式化输出方法
    # ============================================

    @staticmethod
    def format_work(work: Dict) -> str:
        """格式化作品信息为字符串"""
        title = work.get('title', 'Unknown')
        year = work.get('first_publish_year', 'Unknown')

        # 如果有语言统计信息，添加到输出
        lang_count = work.get('_language_count', 0)
        lang_info = f" [{lang_count} languages]" if lang_count > 0 else ""

        # 如果有页数信息，添加到输出
        pages = work.get('_max_pages', 0)
        page_info = f" [{pages}p]" if pages > 0 else ""

        return f"{title} ({year}){lang_info}{page_info}"

    @staticmethod
    def format_edition(edition: Dict) -> str:
        """格式化版本信息为字符串"""
        title = edition.get('title', 'Unknown')
        publish_date = edition.get('publish_date', 'Unknown')
        publishers = ', '.join(edition.get('publishers', ['Unknown']))
        pages = edition.get('number_of_pages', '')
        page_info = f", {pages}p" if pages else ""

        # 语言信息
        languages = edition.get('languages', [])
        lang_str = ""
        if languages:
            lang_codes = []
            for lang in languages:
                if isinstance(lang, dict):
                    lang_codes.append(lang.get('key', '').replace('/languages/', ''))
                else:
                    lang_codes.append(str(lang))
            if lang_codes:
                lang_str = f" [{', '.join(lang_codes)}]"

        return f"{title} - {publishers} ({publish_date}){page_info}{lang_str}"

    # ============================================
    # 实现抽象方法
    # ============================================

    def fetch(self, **kwargs) -> Tuple[List, Dict, str]:
        author_key = kwargs.get('author_key')
        work_id = kwargs.get('work_id')

        if author_key:
            works, api_info, question = self.fetch_author_works(author_key, kwargs.get('max_works', 1000))
            # 转换为字符串格式以兼容旧接口
            works_str = [self.format_work(w) for w in works]
            return works_str, api_info, question
        elif work_id:
            editions, api_info, question = self.fetch_book_editions(work_id, kwargs.get('max_editions', 500))
            # 转换为字符串格式以兼容旧接口
            editions_str = [self.format_edition(e) for e in editions]
            return editions_str, api_info, question

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
