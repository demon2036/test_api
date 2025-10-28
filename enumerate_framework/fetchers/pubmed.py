"""PubMed/NCBI API Fetcher

改进版本：支持ORCID ID查询以确保精确性。

重要：
- 推荐使用ORCID ID而非作者名字，以符合"列举全部"的精确性要求
- PubMed Computed Authors (2024) 提供2100万+消歧的作者
- 作者名字搜索可能不精确（同名、拼写变化等）
"""

import requests
import time
from typing import List, Dict, Tuple
from .base import BaseFetcher


class PubMedFetcher(BaseFetcher):
    """PubMed学术论文获取器

    支持两种查询方式：
    1. ORCID ID（推荐）- 精确且完整
    2. 作者名字（不推荐）- 可能不精确
    """

    def fetch_by_orcid(self, orcid: str, max_results: int = 10000) -> Tuple[List[str], Dict, str]:
        """通过ORCID ID获取作者的所有出版物（推荐方法）

        Args:
            orcid: ORCID ID (格式: "0000-0003-0799-4776")
            max_results: 最大结果数（默认10000）

        Returns:
            (publications, api_info, question)
        """
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

        api_info = {
            "api_endpoint": search_url,
            "method": "GET",
            "parameters": {
                "db": "pubmed",
                "term": f"{orcid}[auid]",
                "retmax": max_results,
                "retmode": "json"
            },
            "authentication": "None (API key recommended for higher rate limits)",
            "rate_limit": "3 requests/second without API key, 10/second with key",
            "documentation": "https://www.ncbi.nlm.nih.gov/books/NBK25500/",
            "orcid_info": "使用ORCID确保精确性，符合'列举全部'理念"
        }

        try:
            # Search using ORCID
            search_params = {
                "db": "pubmed",
                "term": f"{orcid}[auid]",
                "retmax": max_results,
                "retmode": "json"
            }

            search_response = requests.get(search_url, params=search_params, timeout=15)
            if search_response.status_code != 200:
                return [], api_info, ""

            search_data = search_response.json()
            pmids = search_data.get('esearchresult', {}).get('idlist', [])

            if not pmids:
                print(f"  ⚠️  ORCID {orcid} 未找到任何出版物")
                return [], api_info, ""

            # Fetch details in batches
            publications = self._fetch_publication_details(pmids)

            question = f"列出PubMed上ORCID {orcid}的所有出版物（精确查询）"
            return publications, api_info, question

        except Exception as e:
            print(f"  ✗ PubMed ORCID查询错误 ({orcid}): {e}")

        return [], api_info, ""

    def fetch_author_publications(self, author: str, max_results: int = 2000) -> Tuple[List[str], Dict, str]:
        """通过作者名字获取出版物（不推荐 - 可能不精确）

        警告：此方法使用作者名字文本搜索，可能包含同名作者或遗漏某些出版物。
        推荐使用 fetch_by_orcid() 方法获取精确结果。

        Args:
            author: 作者名字（例如: "Fauci AS"）
            max_results: 最大结果数

        Returns:
            (publications, api_info, question)
        """
        print(f"  ⚠️  警告: 使用作者名字搜索可能不精确")
        print(f"     推荐使用ORCID ID以确保精确性")

        # Step 1: Search for publications
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

        api_info = {
            "api_endpoint": search_url,
            "method": "GET",
            "parameters": {
                "db": "pubmed",
                "term": f"{author}[Author]",
                "retmax": max_results,
                "retmode": "json"
            },
            "authentication": "None (API key recommended for higher rate limits)",
            "rate_limit": "3 requests/second without API key, 10/second with key",
            "documentation": "https://www.ncbi.nlm.nih.gov/books/NBK25500/",
            "warning": "作者名字搜索可能不精确，推荐使用ORCID"
        }

        try:
            # Search for all PMIDs
            search_params = {
                "db": "pubmed",
                "term": f"{author}[Author]",
                "retmax": max_results,
                "retmode": "json"
            }

            search_response = requests.get(search_url, params=search_params, timeout=15)
            if search_response.status_code != 200:
                return [], api_info, ""

            search_data = search_response.json()
            pmids = search_data.get('esearchresult', {}).get('idlist', [])

            if not pmids:
                return [], api_info, ""

            # Fetch details using shared method
            publications = self._fetch_publication_details(pmids)

            question = f"列出PubMed上作者{author}的所有出版物（警告: 可能不完整）"
            return publications, api_info, question

        except Exception as e:
            print(f"  ✗ PubMed API错误 ({author}): {e}")

        return [], api_info, ""

    def _fetch_publication_details(self, pmids: List[str]) -> List[str]:
        """从PMID列表获取出版物详情（内部辅助方法）

        Args:
            pmids: PubMed ID列表

        Returns:
            出版物列表（格式："标题 (年份)"）
        """
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        publications = []
        batch_size = 200  # PubMed recommends max 200 per request

        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i+batch_size]
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(batch_pmids),
                "retmode": "xml",
                "rettype": "abstract"
            }

            try:
                fetch_response = requests.get(fetch_url, params=fetch_params, timeout=15)
                if fetch_response.status_code == 200:
                    # Parse XML to extract titles
                    text = fetch_response.text
                    import re
                    titles = re.findall(r'<ArticleTitle>(.*?)</ArticleTitle>', text, re.DOTALL)
                    years = re.findall(r'<Year>(\d{4})</Year>', text)

                    for j, title in enumerate(titles):
                        year = years[j] if j < len(years) else 'Unknown'
                        publications.append(f"{title.strip()} ({year})")

                time.sleep(0.34)  # Respect rate limit (3 req/sec)

            except Exception as e:
                print(f"  ⚠️  批量获取详情时出错: {e}")
                continue

        return publications

    def _fetch_publication_metadata(self, pmids: List[str]) -> List[Dict]:
        """从PMID列表获取完整的出版物元数据（内部辅助方法）

        Args:
            pmids: PubMed ID列表

        Returns:
            出版物元数据列表，每个包含：
            - pmid: PubMed ID
            - title: 标题
            - authors: 作者列表（字典包含name和是否是corresponding author）
            - year: 发表年份
            - journal: 期刊名
            - article_types: 文章类型列表
            - doi: DOI (如果有)
        """
        import xml.etree.ElementTree as ET

        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        publications = []
        batch_size = 200  # PubMed recommends max 200 per request

        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i+batch_size]
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(batch_pmids),
                "retmode": "xml",
                "rettype": "abstract"
            }

            try:
                fetch_response = requests.get(fetch_url, params=fetch_params, timeout=15)
                if fetch_response.status_code == 200:
                    # Parse XML
                    root = ET.fromstring(fetch_response.content)

                    # 遍历每篇文章
                    for article in root.findall('.//PubmedArticle'):
                        pub_metadata = {}

                        # PMID
                        pmid_elem = article.find('.//PMID')
                        pub_metadata['pmid'] = pmid_elem.text if pmid_elem is not None else ''

                        # 标题
                        title_elem = article.find('.//ArticleTitle')
                        pub_metadata['title'] = title_elem.text.strip() if title_elem is not None and title_elem.text else 'Unknown'

                        # 年份
                        year_elem = article.find('.//PubDate/Year')
                        pub_metadata['year'] = int(year_elem.text) if year_elem is not None and year_elem.text else None

                        # 期刊名
                        journal_elem = article.find('.//Journal/Title')
                        pub_metadata['journal'] = journal_elem.text.strip() if journal_elem is not None and journal_elem.text else ''

                        # 作者列表
                        authors = []
                        author_list = article.find('.//AuthorList')
                        if author_list is not None:
                            for author_elem in author_list.findall('Author'):
                                lastname = author_elem.find('LastName')
                                forename = author_elem.find('ForeName')

                                if lastname is not None and lastname.text:
                                    author_name = lastname.text
                                    if forename is not None and forename.text:
                                        author_name = f"{forename.text} {author_name}"

                                    # 检查是否是通讯作者
                                    # 注意：通讯作者信息可能在Affiliation或者通过email标记
                                    # PubMed XML中通讯作者标记不统一，这里简化处理
                                    is_corresponding = False
                                    affiliation = author_elem.find('.//Affiliation')
                                    if affiliation is not None and affiliation.text:
                                        # 通讯作者通常在affiliation中有email
                                        if '@' in affiliation.text:
                                            is_corresponding = True

                                    authors.append({
                                        'name': author_name,
                                        'is_corresponding': is_corresponding
                                    })

                        pub_metadata['authors'] = authors

                        # 文章类型
                        article_types = []
                        pub_type_list = article.find('.//PublicationTypeList')
                        if pub_type_list is not None:
                            for pub_type in pub_type_list.findall('PublicationType'):
                                if pub_type.text:
                                    article_types.append(pub_type.text.strip())
                        pub_metadata['article_types'] = article_types

                        # DOI
                        doi = ''
                        for article_id in article.findall('.//ArticleId'):
                            if article_id.get('IdType') == 'doi':
                                doi = article_id.text
                                break
                        pub_metadata['doi'] = doi

                        publications.append(pub_metadata)

                time.sleep(0.34)  # Respect rate limit (3 req/sec)

            except Exception as e:
                print(f"  ⚠️  批量获取元数据时出错: {e}")
                continue

        return publications

    def fetch_by_orcid_with_metadata(self, orcid: str, max_results: int = 10000) -> Tuple[List[Dict], Dict, str]:
        """通过ORCID ID获取作者的所有出版物（包含完整元数据）

        Args:
            orcid: ORCID ID (格式: "0000-0003-0799-4776")
            max_results: 最大结果数（默认10000）

        Returns:
            (publications_with_metadata, api_info, question)
        """
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

        api_info = {
            "api_endpoint": search_url,
            "method": "GET",
            "parameters": {
                "db": "pubmed",
                "term": f"{orcid}[auid]",
                "retmax": max_results,
                "retmode": "json"
            },
            "authentication": "None (API key recommended for higher rate limits)",
            "rate_limit": "3 requests/second without API key, 10/second with key",
            "documentation": "https://www.ncbi.nlm.nih.gov/books/NBK25500/",
            "orcid_info": "使用ORCID确保精确性，符合'列举全部'理念",
            "metadata_fields": ["pmid", "title", "authors", "year", "journal", "article_types", "doi"]
        }

        try:
            # Search using ORCID
            search_params = {
                "db": "pubmed",
                "term": f"{orcid}[auid]",
                "retmax": max_results,
                "retmode": "json"
            }

            search_response = requests.get(search_url, params=search_params, timeout=15)
            if search_response.status_code != 200:
                return [], api_info, ""

            search_data = search_response.json()
            pmids = search_data.get('esearchresult', {}).get('idlist', [])

            if not pmids:
                print(f"  ⚠️  ORCID {orcid} 未找到任何出版物")
                return [], api_info, ""

            # Fetch metadata
            publications = self._fetch_publication_metadata(pmids)

            question = f"列出PubMed上ORCID {orcid}的所有出版物（包含完整元数据）"
            return publications, api_info, question

        except Exception as e:
            print(f"  ✗ PubMed ORCID查询错误 ({orcid}): {e}")

        return [], api_info, ""

    def fetch_journal_articles(self, journal: str, year: int, max_results: int = 1000) -> Tuple[List[str], Dict, str]:
        """获取期刊某年的所有文章"""
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

        api_info = {
            "api_endpoint": search_url,
            "method": "GET",
            "parameters": {
                "db": "pubmed",
                "term": f"{journal}[Journal] AND {year}[PDAT]",
                "retmax": max_results,
                "retmode": "json"
            },
            "authentication": "None",
            "rate_limit": "3 requests/second",
            "documentation": "https://www.ncbi.nlm.nih.gov/books/NBK25500/"
        }

        try:
            search_params = {
                "db": "pubmed",
                "term": f"{journal}[Journal] AND {year}[PDAT]",
                "retmax": max_results,
                "retmode": "json"
            }

            search_response = requests.get(search_url, params=search_params, timeout=15)
            if search_response.status_code != 200:
                return [], api_info, ""

            search_data = search_response.json()
            pmids = search_data.get('esearchresult', {}).get('idlist', [])

            if not pmids:
                return [], api_info, ""

            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            articles = []
            batch_size = 200

            for i in range(0, len(pmids), batch_size):
                batch_pmids = pmids[i:i+batch_size]
                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(batch_pmids),
                    "retmode": "xml"
                }

                fetch_response = requests.get(fetch_url, params=fetch_params, timeout=15)
                if fetch_response.status_code == 200:
                    text = fetch_response.text
                    import re
                    titles = re.findall(r'<ArticleTitle>(.*?)</ArticleTitle>', text, re.DOTALL)
                    articles.extend([title.strip() for title in titles])

                time.sleep(0.34)

            question = f"列出PubMed上期刊{journal}在{year}年的所有文章"
            return articles, api_info, question

        except Exception as e:
            print(f"  ✗ PubMed API错误 ({journal}, {year}): {e}")

        return [], api_info, ""

    def filter_by_author_role(self, publications_with_metadata: List[Dict], role: str = 'corresponding') -> List[Dict]:
        """过滤指定作者角色的论文

        Args:
            publications_with_metadata: 带元数据的出版物列表
            role: 作者角色 ('corresponding' 表示通讯作者)

        Returns:
            过滤后的出版物列表
        """
        if role == 'corresponding':
            return [p for p in publications_with_metadata
                    if any(author.get('is_corresponding', False) for author in p.get('authors', []))]
        return publications_with_metadata

    def filter_by_article_type(self, publications_with_metadata: List[Dict], article_type: str) -> List[Dict]:
        """过滤指定文章类型的论文

        Args:
            publications_with_metadata: 带元数据的出版物列表
            article_type: 文章类型（如 "Review", "Meta-Analysis", "Clinical Trial" 等）
                         支持部分匹配，不区分大小写

        Returns:
            过滤后的出版物列表
        """
        article_type_lower = article_type.lower()
        return [p for p in publications_with_metadata
                if any(article_type_lower in atype.lower()
                      for atype in p.get('article_types', []))]

    def filter_by_journal(self, publications_with_metadata: List[Dict], journal: str) -> List[Dict]:
        """过滤指定期刊的论文

        Args:
            publications_with_metadata: 带元数据的出版物列表
            journal: 期刊名称（支持部分匹配，不区分大小写）

        Returns:
            过滤后的出版物列表
        """
        journal_lower = journal.lower()
        return [p for p in publications_with_metadata
                if journal_lower in p.get('journal', '').lower()]

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
            result = [p for p in result if p.get('year') and p['year'] >= min_year]
        if max_year is not None:
            result = [p for p in result if p.get('year') and p['year'] <= max_year]
        return result

    # 实现抽象方法
    def fetch(self, **kwargs) -> Tuple[List[str], Dict, str]:
        """统一的fetch接口

        Args:
            orcid: ORCID ID（推荐）
            author: 作者名字（不推荐）
            journal: 期刊名
            year: 年份
            max_results: 最大结果数
        """
        if kwargs.get('orcid'):
            # 推荐方式：使用ORCID
            return self.fetch_by_orcid(
                kwargs['orcid'],
                kwargs.get('max_results', 10000)
            )
        elif kwargs.get('author'):
            # 不推荐方式：使用作者名字
            return self.fetch_author_publications(
                kwargs['author'],
                kwargs.get('max_results', 2000)
            )
        elif kwargs.get('journal') and kwargs.get('year'):
            return self.fetch_journal_articles(kwargs['journal'], kwargs['year'])
        return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        if kwargs.get('orcid'):
            return f"pubmed_orcid_{kwargs['orcid'].replace('-', '_')}"
        elif kwargs.get('author'):
            return f"pubmed_{kwargs['author'].replace(' ', '_')}"
        elif kwargs.get('journal'):
            return f"pubmed_{kwargs['journal'].replace(' ', '_')}_{kwargs.get('year', '')}"
        return "pubmed_unknown"

    def get_metadata(self, **kwargs) -> Dict:
        return {
            "orcid": kwargs.get('orcid'),
            "author": kwargs.get('author'),
            "journal": kwargs.get('journal'),
            "year": kwargs.get('year'),
            "platform": "PubMed",
            "identifier_type": "ORCID (推荐)" if kwargs.get('orcid') else "作者名字（不精确）"
        }
