"""Zenodo Research Data Repository API Fetcher"""

import requests
from typing import List, Dict, Tuple
from ..base import BaseFetcher


class ZenodoFetcher(BaseFetcher):
    """Zenodo研究数据获取器"""

    def fetch(self, orcid: str = None, creator_name: str = None, community_id: str = None, max_records: int = 1000) -> Tuple[List[str], Dict, str]:
        """通用fetch方法 - 优先使用ORCID"""
        if orcid:
            return self.fetch_by_orcid(orcid, max_records)
        elif creator_name:
            return self.fetch_by_creator(creator_name, max_records)
        elif community_id:
            return self.fetch_by_community(community_id, max_records)
        else:
            raise ValueError("必须提供orcid, creator_name或community_id参数之一")

    def fetch_by_creator(self, creator_name: str, max_records: int = 1000) -> Tuple[List[str], Dict, str]:
        """通过创建者名字获取所有记录（不推荐 - 使用ORCID更精确）

        Args:
            creator_name: 创建者名字
            max_records: 最大获取记录数
        """
        print(f"  ⚠️  警告: 使用创建者名字搜索可能不精确")
        print(f"     推荐使用ORCID ID以确保精确性")

        return self._fetch_records(f'creators.name:"{creator_name}"', max_records)

    def fetch_by_orcid(self, orcid: str, max_records: int = 1000) -> Tuple[List[str], Dict, str]:
        """通过ORCID ID获取研究者的所有记录（推荐方法）

        Args:
            orcid: ORCID ID (e.g., "0000-0002-1825-0097")
            max_records: 最大获取记录数
        """
        return self._fetch_records(f'creators.orcid:"{orcid}"', max_records)

    def fetch_by_community(self, community_id: str, max_records: int = 1000) -> Tuple[List[str], Dict, str]:
        """获取某个社区的所有记录

        Args:
            community_id: 社区ID (e.g., "zenodo")
            max_records: 最大获取记录数
        """
        return self._fetch_records(f'communities:"{community_id}"', max_records)

    def _fetch_records(self, query: str, max_records: int) -> Tuple[List[str], Dict, str]:
        """内部方法：执行Zenodo API查询"""
        api_url = "https://zenodo.org/api/records"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"q": query},
            "authentication": "Optional (API token for higher rate limits)",
            "rate_limit": "60 requests/minute (anonymous), 100 requests/minute (authenticated)",
            "documentation": "https://developers.zenodo.org/"
        }

        records = []
        page = 1
        page_size = 100  # Max allowed by Zenodo

        try:
            while len(records) < max_records:
                params = {
                    "q": query,
                    "size": min(page_size, max_records - len(records)),
                    "page": page,
                    "all_versions": True  # Include all versions of records
                }

                response = requests.get(api_url, params=params, timeout=15)
                if response.status_code != 200:
                    print(f"  ✗ Zenodo API错误: HTTP {response.status_code}")
                    break

                data = response.json()
                hits = data.get('hits', {}).get('hits', [])

                if not hits:
                    break

                for record in hits:
                    # 基本信息
                    doi = record.get('doi', 'Unknown')
                    metadata = record.get('metadata', {})
                    title = metadata.get('title', 'Unknown')
                    pub_date = metadata.get('publication_date', 'Unknown')

                    # 扩展元数据
                    resource_type = metadata.get('resource_type', {}).get('type', 'unknown')

                    # 文件大小（累计所有文件）
                    files = record.get('files', [])
                    total_size = sum(f.get('size', 0) for f in files)

                    # 许可证信息
                    license_info = metadata.get('license', {})
                    license_id = license_info.get('id', 'unknown')

                    # 创建详细记录（字符串格式，向后兼容）
                    records.append(f"[{doi}] {title} ({pub_date})")

                if len(hits) < page_size:
                    break

                page += 1

            question = f"列出Zenodo上符合查询 '{query}' 的所有记录"
            return records, api_info, question

        except Exception as e:
            print(f"  ✗ Zenodo API错误: {e}")

        return [], api_info, ""

    def _fetch_records_with_metadata(self, query: str, max_records: int) -> Tuple[List[Dict], Dict, str]:
        """内部方法：执行Zenodo API查询并返回完整元数据

        Returns:
            每个record包含：
            - doi: DOI
            - title: 标题
            - publication_date: 发布日期
            - resource_type: 资源类型（dataset, software, publication等）
            - total_size_bytes: 总文件大小（字节）
            - license: 许可证ID
            - creators: 创建者列表
            - description: 描述
        """
        api_url = "https://zenodo.org/api/records"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"q": query},
            "authentication": "Optional (API token for higher rate limits)",
            "rate_limit": "60 requests/minute (anonymous), 100 requests/minute (authenticated)",
            "documentation": "https://developers.zenodo.org/",
            "metadata_fields": ["doi", "title", "publication_date", "resource_type", "total_size_bytes", "license", "creators", "description"]
        }

        records = []
        page = 1
        page_size = 100  # Max allowed by Zenodo

        try:
            while len(records) < max_records:
                params = {
                    "q": query,
                    "size": min(page_size, max_records - len(records)),
                    "page": page,
                    "all_versions": True  # Include all versions of records
                }

                response = requests.get(api_url, params=params, timeout=15)
                if response.status_code != 200:
                    print(f"  ✗ Zenodo API错误: HTTP {response.status_code}")
                    break

                data = response.json()
                hits = data.get('hits', {}).get('hits', [])

                if not hits:
                    break

                for record in hits:
                    # 基本信息
                    metadata = record.get('metadata', {})

                    # 文件大小（累计所有文件）
                    files = record.get('files', [])
                    total_size = sum(f.get('size', 0) for f in files)

                    # 许可证信息
                    license_info = metadata.get('license', {})

                    # 创建者信息
                    creators = []
                    for creator in metadata.get('creators', []):
                        creators.append({
                            'name': creator.get('name', ''),
                            'orcid': creator.get('orcid', '')
                        })

                    # 资源类型详情
                    resource_type_obj = metadata.get('resource_type', {})

                    record_metadata = {
                        'doi': record.get('doi', ''),
                        'title': metadata.get('title', 'Unknown'),
                        'publication_date': metadata.get('publication_date', ''),
                        'resource_type': resource_type_obj.get('type', 'unknown'),
                        'resource_subtype': resource_type_obj.get('subtype', ''),
                        'total_size_bytes': total_size,
                        'license': license_info.get('id', 'unknown'),
                        'creators': creators,
                        'description': metadata.get('description', '')[:500],  # 限制描述长度
                        'keywords': metadata.get('keywords', []),
                        'version': metadata.get('version', '')
                    }

                    records.append(record_metadata)

                if len(hits) < page_size:
                    break

                page += 1

            question = f"列出Zenodo上符合查询 '{query}' 的所有记录（包含完整元数据）"
            return records, api_info, question

        except Exception as e:
            print(f"  ✗ Zenodo API错误: {e}")

        return [], api_info, ""

    def fetch_by_orcid_with_metadata(self, orcid: str, max_records: int = 1000) -> Tuple[List[Dict], Dict, str]:
        """通过ORCID ID获取研究者的所有记录（包含完整元数据）

        Args:
            orcid: ORCID ID (e.g., "0000-0002-1825-0097")
            max_records: 最大获取记录数
        """
        return self._fetch_records_with_metadata(f'creators.orcid:"{orcid}"', max_records)

    def filter_by_size(self, records_with_metadata: List[Dict], min_size_bytes: int = None, min_size_gb: float = None) -> List[Dict]:
        """过滤指定文件大小的记录

        Args:
            records_with_metadata: 带元数据的记录列表
            min_size_bytes: 最小文件大小（字节）
            min_size_gb: 最小文件大小（GB），如果提供则优先使用

        Returns:
            过滤后的记录列表
        """
        if min_size_gb is not None:
            min_size_bytes = int(min_size_gb * 1024 * 1024 * 1024)

        if min_size_bytes is None:
            return records_with_metadata

        return [r for r in records_with_metadata
                if r.get('total_size_bytes', 0) >= min_size_bytes]

    def filter_by_resource_type(self, records_with_metadata: List[Dict], resource_type: str) -> List[Dict]:
        """过滤指定资源类型的记录

        Args:
            records_with_metadata: 带元数据的记录列表
            resource_type: 资源类型（dataset, software, publication, poster, presentation等）
                          支持部分匹配，不区分大小写

        Returns:
            过滤后的记录列表
        """
        resource_type_lower = resource_type.lower()
        return [r for r in records_with_metadata
                if resource_type_lower in r.get('resource_type', '').lower()]

    def filter_by_license(self, records_with_metadata: List[Dict], license_pattern: str) -> List[Dict]:
        """过滤指定许可证的记录

        Args:
            records_with_metadata: 带元数据的记录列表
            license_pattern: 许可证模式（如 "cc", "cc-by", "mit"等）
                           支持部分匹配，不区分大小写

        Returns:
            过滤后的记录列表
        """
        license_lower = license_pattern.lower()
        return [r for r in records_with_metadata
                if license_lower in r.get('license', '').lower()]

    def filter_by_year(self, records_with_metadata: List[Dict],
                      min_year: int = None, max_year: int = None) -> List[Dict]:
        """过滤指定年份范围的记录

        Args:
            records_with_metadata: 带元数据的记录列表
            min_year: 最小年份（包含）
            max_year: 最大年份（包含）

        Returns:
            过滤后的记录列表
        """
        result = records_with_metadata
        if min_year is not None:
            result = [r for r in result
                     if r.get('publication_date', '')[:4].isdigit() and
                     int(r['publication_date'][:4]) >= min_year]
        if max_year is not None:
            result = [r for r in result
                     if r.get('publication_date', '')[:4].isdigit() and
                     int(r['publication_date'][:4]) <= max_year]
        return result

    def get_domain_name(self, identifier: str) -> str:
        return f"zenodo_{identifier.replace('-', '_').replace(':', '_')}"

    def get_metadata(self, identifier: str) -> Dict:
        return {"identifier": identifier, "repository": "Zenodo (CERN)"}
