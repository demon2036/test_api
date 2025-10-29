"""Crates.io API Fetcher"""

import requests
from typing import List, Dict, Tuple
from ..base import BaseFetcher


class CratesFetcher(BaseFetcher):
    """Rust Crates.io包版本获取器"""

    def fetch(self, crate: str) -> Tuple[List[str], Dict, str]:
        api_url = f"https://crates.io/api/v1/crates/{crate}"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "1 req/sec recommended",
            "documentation": "https://crates.io/data-access"
        }
        try:
            headers = {'User-Agent': 'enumerate-test-framework'}
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                versions = [v['num'] for v in data['versions']]
                question = f"列出Rust {crate}库在crates.io上的所有版本"
                return versions, api_info, question
        except Exception as e:
            print(f"  ✗ Crates.io API错误 ({crate}): {e}")
        return [], api_info, ""

    def fetch_with_metadata(self, crate: str) -> Tuple[List[Dict], Dict, str]:
        """获取Crates.io包的所有版本（包含完整元数据）

        Args:
            crate: Crate名称

        Returns:
            (versions_with_metadata, api_info, question)
            每个version是一个字典，包含：
            - version: 版本号
            - created_at: 创建时间
            - yanked: 是否被撤回
            - downloads: 下载量
        """
        api_url = f"https://crates.io/api/v1/crates/{crate}"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "1 req/sec recommended",
            "documentation": "https://crates.io/data-access",
            "metadata_fields": ["version", "created_at", "yanked", "downloads"]
        }

        versions_with_metadata = []

        try:
            headers = {'User-Agent': 'enumerate-test-framework'}
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()

                for v in data.get('versions', []):
                    version_metadata = {
                        "version": v.get('num', ''),
                        "created_at": v.get('created_at', ''),
                        "yanked": v.get('yanked', False),
                        "downloads": v.get('downloads', 0),
                        "license": v.get('license', '')
                    }
                    versions_with_metadata.append(version_metadata)

                question = f"列出Rust {crate}库在crates.io上的所有版本"
                return versions_with_metadata, api_info, question

        except Exception as e:
            print(f"  ✗ Crates.io API错误 ({crate}): {e}")

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
                if v['created_at'] and v['created_at'].startswith(str(year))]

    def filter_by_yanked(self, versions_with_metadata: List[Dict], yanked: bool = True) -> List[Dict]:
        """过滤被撤回的版本

        Args:
            versions_with_metadata: 带元数据的版本列表
            yanked: True返回被撤回的版本，False返回正常版本

        Returns:
            过滤后的版本列表
        """
        return [v for v in versions_with_metadata
                if v['yanked'] == yanked]

    def filter_prerelease_versions(self, versions_with_metadata: List[Dict]) -> List[Dict]:
        """识别预发布版本（包含alpha, beta, rc等标记）

        Args:
            versions_with_metadata: 带元数据的版本列表

        Returns:
            预发布版本列表
        """
        prerelease_keywords = ['alpha', 'beta', 'rc', 'pre', 'preview', 'dev']

        prerelease_versions = []
        for v in versions_with_metadata:
            version = v['version'].lower()
            if any(keyword in version for keyword in prerelease_keywords):
                prerelease_versions.append(v)

        return prerelease_versions

    def filter_stable_versions(self, versions_with_metadata: List[Dict]) -> List[Dict]:
        """过滤稳定版本（排除预发布版本）

        Args:
            versions_with_metadata: 带元数据的版本列表

        Returns:
            稳定版本列表
        """
        prerelease_keywords = ['alpha', 'beta', 'rc', 'pre', 'preview', 'dev']

        stable_versions = []
        for v in versions_with_metadata:
            version = v['version'].lower()
            if not any(keyword in version for keyword in prerelease_keywords):
                stable_versions.append(v)

        return stable_versions

    def get_domain_name(self, crate: str, **kwargs) -> str:
        return f"crates_{crate}"

    def get_metadata(self, crate: str, **kwargs) -> Dict:
        return {"crate": crate, "ecosystem": "Rust/Crates.io"}
