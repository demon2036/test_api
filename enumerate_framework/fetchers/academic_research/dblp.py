"""DBLP (计算机科学文献数据库) API Fetcher

DBLP提供精确的作者标识符（PID）系统，完全符合"列举全部"的理念。
每个作者有唯一的PID，永不改变，可以精确枚举所有出版物。
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple
from ..base import BaseFetcher


class DBLPFetcher(BaseFetcher):
    """DBLP计算机科学文献数据库获取器

    使用PID（永久标识符）而非作者名字，确保精确性。

    示例PID：
    - Yann LeCun: "l/YannLeCun"
    - Donald Knuth: "k/DonaldEKnuth"
    - Geoffrey Hinton: "h/GeoffreyEHinton"
    """

    def fetch_by_pid(self, pid: str, max_publications: int = 10000) -> Tuple[List[str], Dict, str]:
        """通过PID获取作者的所有出版物

        Args:
            pid: DBLP永久标识符（例如: "l/YannLeCun"）
            max_publications: 最大获取数量（默认10000，实际返回所有）

        Returns:
            (publications, api_info, question)
        """
        # 使用XML格式（更可靠）
        api_url = f"https://dblp.org/pid/{pid}.xml"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"pid": pid},
            "authentication": "None",
            "rate_limit": "No official limit (但请勿滥用)",
            "documentation": "https://dblp.org/faq/",
            "pid_description": "PID是永久标识符，永不改变，确保精确查询"
        }

        publications = []

        try:
            response = requests.get(api_url, timeout=30)

            if response.status_code == 200:
                # 解析XML
                root = ET.fromstring(response.content)

                # 查找所有publication条目
                # DBLP XML格式: <person> -> <r> (publications)
                for r_elem in root.findall('./r'):
                    # 每个<r>包含一个publication (article, inproceedings, etc.)
                    for pub_elem in r_elem:
                        # 提取标题
                        title_elem = pub_elem.find('title')
                        if title_elem is not None and title_elem.text:
                            title = title_elem.text.strip()

                            # 提取年份（如果有）
                            year_elem = pub_elem.find('year')
                            year = year_elem.text.strip() if year_elem is not None and year_elem.text else ""

                            # 提取出版物类型
                            pub_type = pub_elem.tag

                            # 格式化
                            if year:
                                publications.append(f"[{pub_type}] {title} ({year})")
                            else:
                                publications.append(f"[{pub_type}] {title}")

                            if len(publications) >= max_publications:
                                break

                    if len(publications) >= max_publications:
                        break

                # 提取作者名字（用于问题描述）
                person_elem = root.find('./person')
                author_name = person_elem.get('name', pid) if person_elem is not None else pid

                question = f"列出DBLP中作者{author_name} (PID: {pid})的所有出版物"
                return publications, api_info, question

            elif response.status_code == 404:
                print(f"  ✗ DBLP PID '{pid}' 不存在")
                print(f"    提示: 访问 https://dblp.org 搜索作者获取正确的PID")

        except ET.ParseError as e:
            print(f"  ✗ DBLP XML解析错误: {e}")
        except Exception as e:
            print(f"  ✗ DBLP API错误 (PID {pid}): {e}")

        return [], api_info, ""

    def fetch_with_metadata(self, pid: str, max_publications: int = 10000) -> Tuple[List[Dict], Dict, str]:
        """通过PID获取作者的所有出版物（包含完整元数据）

        Args:
            pid: DBLP永久标识符（例如: "l/YannLeCun"）
            max_publications: 最大获取数量（默认10000，实际返回所有）

        Returns:
            (publications_with_metadata, api_info, question)
            每个publication是一个字典，包含：
            - title: 标题
            - authors: 作者列表
            - author_position: 该作者在作者列表中的位置（1-based）
            - year: 发表年份
            - venue: 会议/期刊名称
            - type: 出版物类型（article/inproceedings/incollection等）
            - ee: 电子版链接（如果有）
        """
        api_url = f"https://dblp.org/pid/{pid}.xml"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"pid": pid},
            "authentication": "None",
            "rate_limit": "No official limit (但请勿滥用)",
            "documentation": "https://dblp.org/faq/",
            "pid_description": "PID是永久标识符，永不改变，确保精确查询",
            "metadata_fields": ["title", "authors", "author_position", "year", "venue", "type", "ee"]
        }

        publications_with_metadata = []

        try:
            response = requests.get(api_url, timeout=30)

            if response.status_code == 200:
                root = ET.fromstring(response.content)

                # 获取作者名字
                person_elem = root.find('./person')
                target_author_name = person_elem.get('name', '') if person_elem is not None else ''

                # 遍历所有出版物
                for r_elem in root.findall('./r'):
                    for pub_elem in r_elem:
                        # 提取标题
                        title_elem = pub_elem.find('title')
                        if title_elem is None or not title_elem.text:
                            continue

                        title = title_elem.text.strip()

                        # 提取所有作者
                        authors = []
                        author_position = -1
                        for i, author_elem in enumerate(pub_elem.findall('author'), start=1):
                            if author_elem.text:
                                author_name = author_elem.text.strip()
                                authors.append(author_name)
                                # 检查是否是目标作者
                                if target_author_name and author_name == target_author_name:
                                    author_position = i

                        # 提取年份
                        year_elem = pub_elem.find('year')
                        year = int(year_elem.text.strip()) if year_elem is not None and year_elem.text else None

                        # 提取venue（会议/期刊名称）
                        # 不同类型的出版物，venue字段不同
                        venue = ""
                        if pub_elem.tag == "article":
                            # 期刊文章
                            journal_elem = pub_elem.find('journal')
                            venue = journal_elem.text.strip() if journal_elem is not None and journal_elem.text else ""
                        elif pub_elem.tag == "inproceedings":
                            # 会议论文
                            booktitle_elem = pub_elem.find('booktitle')
                            venue = booktitle_elem.text.strip() if booktitle_elem is not None and booktitle_elem.text else ""
                        elif pub_elem.tag == "incollection":
                            # 书籍章节
                            booktitle_elem = pub_elem.find('booktitle')
                            venue = booktitle_elem.text.strip() if booktitle_elem is not None and booktitle_elem.text else ""

                        # 提取类型
                        pub_type = pub_elem.tag

                        # 提取电子版链接
                        ee_elem = pub_elem.find('ee')
                        ee_link = ee_elem.text.strip() if ee_elem is not None and ee_elem.text else ""

                        # 构建元数据字典
                        pub_metadata = {
                            "title": title,
                            "authors": authors,
                            "author_position": author_position,
                            "year": year,
                            "venue": venue,
                            "type": pub_type,
                            "ee": ee_link
                        }

                        publications_with_metadata.append(pub_metadata)

                        if len(publications_with_metadata) >= max_publications:
                            break

                    if len(publications_with_metadata) >= max_publications:
                        break

                question = f"列出DBLP中作者{target_author_name} (PID: {pid})的所有出版物"
                return publications_with_metadata, api_info, question

            elif response.status_code == 404:
                print(f"  ✗ DBLP PID '{pid}' 不存在")

        except ET.ParseError as e:
            print(f"  ✗ DBLP XML解析错误: {e}")
        except Exception as e:
            print(f"  ✗ DBLP API错误 (PID {pid}): {e}")

        return [], api_info, ""

    def filter_by_author_position(self, publications_with_metadata: List[Dict], position: int) -> List[Dict]:
        """过滤指定作者位置的论文

        Args:
            publications_with_metadata: 带元数据的出版物列表
            position: 作者位置（1表示第一作者，2表示第二作者，-1表示最后一位）

        Returns:
            过滤后的出版物列表
        """
        if position == -1:
            # 最后一位作者
            return [p for p in publications_with_metadata
                    if p['author_position'] == len(p['authors'])]
        else:
            return [p for p in publications_with_metadata
                    if p['author_position'] == position]

    def filter_by_venue(self, publications_with_metadata: List[Dict], venue: str) -> List[Dict]:
        """过滤指定会议/期刊的论文

        Args:
            publications_with_metadata: 带元数据的出版物列表
            venue: 会议/期刊名称（支持部分匹配，不区分大小写）

        Returns:
            过滤后的出版物列表
        """
        venue_lower = venue.lower()
        return [p for p in publications_with_metadata
                if venue_lower in p['venue'].lower()]

    def filter_by_year(self, publications_with_metadata: List[Dict],
                      min_year: int = None, max_year: int = None) -> List[Dict]:
        """过滤指定年份范围的论文

        Args:
            publications_with_metadata: 带元数据的出版物列表
            min_year: 最小年份（包含）
            max_year: 最大年份（包含）

        Returns:
            过滤后的出版物列表
        """
        result = publications_with_metadata
        if min_year is not None:
            result = [p for p in result if p['year'] and p['year'] >= min_year]
        if max_year is not None:
            result = [p for p in result if p['year'] and p['year'] <= max_year]
        return result

    def filter_by_type(self, publications_with_metadata: List[Dict], pub_type: str) -> List[Dict]:
        """过滤指定论文类型

        Args:
            publications_with_metadata: 带元数据的出版物列表
            pub_type: 出版物类型（article, inproceedings, incollection等）

        Returns:
            过滤后的出版物列表
        """
        return [p for p in publications_with_metadata
                if p['type'] == pub_type]

    def search_author(self, author_name: str, max_results: int = 10) -> List[Dict]:
        """搜索作者以获取PID（辅助功能）

        Args:
            author_name: 作者名字
            max_results: 最多返回多少个候选

        Returns:
            候选作者列表: [{"pid": "l/YannLeCun", "name": "Yann LeCun", "affiliations": ...}, ...]
        """
        search_url = "https://dblp.org/search/author/api"

        try:
            params = {
                "q": author_name,
                "format": "json",
                "h": max_results
            }
            response = requests.get(search_url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                authors = []

                hits = data.get('result', {}).get('hits', {}).get('hit', [])
                for hit in hits:
                    info = hit.get('info', {})
                    # 提取URL并转换为PID
                    url = info.get('url', '')
                    # URL格式: https://dblp.org/pid/l/YannLeCun.html
                    if '/pid/' in url:
                        pid = url.split('/pid/')[1].replace('.html', '')
                        authors.append({
                            "pid": pid,
                            "name": info.get('author', ''),
                            "url": url,
                            "notes": info.get('notes', {}).get('note', [])
                        })

                return authors

        except Exception as e:
            print(f"  ✗ DBLP作者搜索错误: {e}")

        return []

    # 实现抽象方法
    def fetch(self, **kwargs) -> Tuple[List[str], Dict, str]:
        """统一的fetch接口

        Args:
            pid: DBLP永久标识符（推荐）
            author_name: 作者名字（将先搜索获取PID）
            max_publications: 最大获取数量
        """
        if 'pid' in kwargs:
            return self.fetch_by_pid(
                kwargs['pid'],
                kwargs.get('max_publications', 10000)
            )
        elif 'author_name' in kwargs:
            # 先搜索PID，然后获取
            print(f"  正在搜索作者 '{kwargs['author_name']}' 的PID...")
            authors = self.search_author(kwargs['author_name'], max_results=1)
            if authors:
                pid = authors[0]['pid']
                print(f"  找到PID: {pid}")
                return self.fetch_by_pid(pid, kwargs.get('max_publications', 10000))
            else:
                print(f"  ✗ 未找到作者 '{kwargs['author_name']}'")
                return [], {}, ""
        else:
            print("  ✗ 需要提供 'pid' 或 'author_name' 参数")
            return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        if 'pid' in kwargs:
            return f"dblp_{kwargs['pid'].replace('/', '_')}"
        elif 'author_name' in kwargs:
            return f"dblp_{kwargs['author_name'].lower().replace(' ', '_')}"
        return "dblp_unknown"

    def get_metadata(self, **kwargs) -> Dict:
        return {
            "pid": kwargs.get('pid'),
            "author_name": kwargs.get('author_name'),
            "platform": "DBLP",
            "identifier_type": "PID (永久标识符)"
        }
