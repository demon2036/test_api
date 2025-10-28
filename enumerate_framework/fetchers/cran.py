"""CRAN (R Packages) API Fetcher"""

import requests
from typing import List, Dict, Tuple
from .base import BaseFetcher


class CRANFetcher(BaseFetcher):
    """CRAN R包版本获取器"""

    def fetch(self, package: str) -> Tuple[List[str], Dict, str]:
        """获取CRAN包的所有版本"""
        api_url = f"https://crandb.r-pkg.org/{package}/all"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://github.com/r-hub/crandb"
        }

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # CRAN API returns versions as keys in the 'versions' object
                versions = list(data.get('versions', {}).keys())
                # Sort versions chronologically (they have timestamps)
                versions.sort()
                question = f"列出CRAN上{package}包的所有发布版本号"
                return versions, api_info, question
            elif response.status_code == 404:
                print(f"  ✗ CRAN包 '{package}' 不存在")
        except Exception as e:
            print(f"  ✗ CRAN API错误 ({package}): {e}")

        return [], api_info, ""

    def fetch_with_metadata(self, package: str) -> Tuple[List[Dict], Dict, str]:
        """获取CRAN包的所有版本（包含元数据）"""
        api_url = f"https://crandb.r-pkg.org/{package}/all"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://github.com/r-hub/crandb",
            "metadata_fields": ["version", "date"]
        }

        versions_with_metadata = []

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                versions_data = data.get('versions', {})

                for version, version_info in versions_data.items():
                    version_metadata = {
                        "version": version,
                        "date": version_info.get('Date', ''),
                        "maintainer": version_info.get('Maintainer', '')
                    }
                    versions_with_metadata.append(version_metadata)

                # Sort by version
                versions_with_metadata.sort(key=lambda x: x['version'])

                question = f"列出CRAN上{package}包的所有发布版本号"
                return versions_with_metadata, api_info, question

            elif response.status_code == 404:
                print(f"  ✗ CRAN包 '{package}' 不存在")

        except Exception as e:
            print(f"  ✗ CRAN API错误 ({package}): {e}")

        return [], api_info, ""

    def filter_by_year(self, versions_with_metadata: List[Dict], year: int) -> List[Dict]:
        """过滤指定年份发布的版本"""
        return [v for v in versions_with_metadata
                if v.get('date') and str(year) in v['date']]

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

    def get_domain_name(self, package: str) -> str:
        return f"cran_{package.replace('-', '_')}"

    def get_metadata(self, package: str) -> Dict:
        return {"package": package, "ecosystem": "R/CRAN"}
