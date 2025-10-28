"""NuGet API Fetcher"""

import requests
from typing import List, Dict, Tuple
from .base import BaseFetcher


class NuGetFetcher(BaseFetcher):
    def fetch(self, package: str) -> Tuple[List[str], Dict, str]:
        api_url = f"https://api.nuget.org/v3-flatcontainer/{package.lower()}/index.json"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://docs.microsoft.com/en-us/nuget/api/overview"
        }
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                versions = data.get('versions', [])
                question = f"列出NuGet上{package}的所有版本"
                return versions, api_info, question
        except Exception as e:
            print(f"  ✗ NuGet API错误 ({package}): {e}")
        return [], api_info, ""

    def fetch_with_metadata(self, package: str) -> Tuple[List[Dict], Dict, str]:
        """获取NuGet包的所有版本（包含元数据）

        Args:
            package: NuGet包名

        Returns:
            (versions_with_metadata, api_info, question)
            每个version是一个字典，包含：
            - version: 版本号
            - published: 发布时间
            - authors: 作者列表
            - description: 描述
        """
        # 使用Registration API来获取更丰富的元数据
        api_url = f"https://api.nuget.org/v3/registration5-semver1/{package.lower()}/index.json"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://docs.microsoft.com/en-us/nuget/api/overview",
            "metadata_fields": ["version", "published", "authors", "description"]
        }

        versions_with_metadata = []

        try:
            response = requests.get(api_url, timeout=15)
            if response.status_code == 200:
                data = response.json()

                # NuGet Registration API返回分页的数据
                for page in data.get('items', []):
                    # 每个page可能包含items（内联）或需要额外请求
                    items = page.get('items', [])

                    # 如果items为空，可能需要从@id获取
                    if not items and '@id' in page:
                        try:
                            page_response = requests.get(page['@id'], timeout=10)
                            if page_response.status_code == 200:
                                page_data = page_response.json()
                                items = page_data.get('items', [])
                        except:
                            continue

                    # 提取每个版本的元数据
                    for item in items:
                        catalog_entry = item.get('catalogEntry', {})

                        version_metadata = {
                            "version": catalog_entry.get('version', ''),
                            "published": catalog_entry.get('published', ''),
                            "authors": catalog_entry.get('authors', ''),
                            "description": catalog_entry.get('description', '')[:100] if catalog_entry.get('description') else ''
                        }
                        versions_with_metadata.append(version_metadata)

                question = f"列出NuGet上{package}的所有版本"
                return versions_with_metadata, api_info, question
            elif response.status_code == 404:
                print(f"  ✗ NuGet包 '{package}' 不存在")

        except Exception as e:
            print(f"  ✗ NuGet API错误 ({package}): {e}")

        return [], api_info, ""

    def filter_by_year(self, versions_with_metadata: List[Dict], year: int) -> List[Dict]:
        """过滤指定年份发布的版本

        Args:
            versions_with_metadata: 带元数据的版本列表
            year: 年份（如2024）

        Returns:
            过滤后的版本列表
        """
        return [v for v in versions_with_metadata
                if v['published'] and v['published'].startswith(str(year))]

    def filter_prerelease_versions(self, versions_with_metadata: List[Dict]) -> List[Dict]:
        """识别预发布版本"""
        prerelease_keywords = ['alpha', 'beta', 'rc', 'pre', 'preview', 'dev']

        prerelease_versions = []
        for v in versions_with_metadata:
            version = v['version'].lower()
            if any(keyword in version for keyword in prerelease_keywords):
                prerelease_versions.append(v)

        return prerelease_versions

    def filter_stable_versions(self, versions_with_metadata: List[Dict]) -> List[Dict]:
        """过滤稳定版本"""
        prerelease_keywords = ['alpha', 'beta', 'rc', 'pre', 'preview', 'dev']

        stable_versions = []
        for v in versions_with_metadata:
            version = v['version'].lower()
            if not any(keyword in version for keyword in prerelease_keywords):
                stable_versions.append(v)

        return stable_versions

    def get_domain_name(self, package: str, **kwargs) -> str:
        return f"nuget_{package.lower().replace('.', '_')}"

    def get_metadata(self, package: str, **kwargs) -> Dict:
        return {"package": package, "ecosystem": ".NET/NuGet"}
