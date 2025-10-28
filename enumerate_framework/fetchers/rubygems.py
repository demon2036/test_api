"""RubyGems API Fetcher"""

import requests
from typing import List, Dict, Tuple
from .base import BaseFetcher


class RubyGemsFetcher(BaseFetcher):
    def fetch(self, gem: str) -> Tuple[List[str], Dict, str]:
        api_url = f"https://rubygems.org/api/v1/versions/{gem}.json"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://guides.rubygems.org/rubygems-org-api/"
        }
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                versions = [v['number'] for v in response.json()]
                question = f"列出Ruby {gem}在RubyGems上的所有版本"
                return versions, api_info, question
        except Exception as e:
            print(f"  ✗ RubyGems API错误 ({gem}): {e}")
        return [], api_info, ""

    def fetch_with_metadata(self, gem: str) -> Tuple[List[Dict], Dict, str]:
        """获取RubyGems的所有版本（包含完整元数据）

        Args:
            gem: Gem名称

        Returns:
            (versions_with_metadata, api_info, question)
            每个version是一个字典，包含：
            - version: 版本号
            - created_at: 创建时间
            - prerelease: 是否为预发布版本
        """
        api_url = f"https://rubygems.org/api/v1/versions/{gem}.json"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://guides.rubygems.org/rubygems-org-api/",
            "metadata_fields": ["version", "created_at", "prerelease"]
        }

        versions_with_metadata = []

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()

                for v in data:
                    version_metadata = {
                        "version": v.get('number', ''),
                        "created_at": v.get('created_at', ''),
                        "prerelease": v.get('prerelease', False),
                        "platform": v.get('platform', 'ruby')
                    }
                    versions_with_metadata.append(version_metadata)

                question = f"列出Ruby {gem}在RubyGems上的所有版本"
                return versions_with_metadata, api_info, question

        except Exception as e:
            print(f"  ✗ RubyGems API错误 ({gem}): {e}")

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

    def filter_prerelease_versions(self, versions_with_metadata: List[Dict]) -> List[Dict]:
        """识别预发布版本

        Args:
            versions_with_metadata: 带元数据的版本列表

        Returns:
            预发布版本列表
        """
        # RubyGems API直接提供prerelease标记
        prerelease_versions = [v for v in versions_with_metadata
                               if v.get('prerelease', False)]

        # 如果API没有prerelease标记，则通过版本号判断
        if not prerelease_versions:
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
        # 使用API的prerelease标记
        stable_versions = [v for v in versions_with_metadata
                          if not v.get('prerelease', False)]

        # 如果API没有提供，则通过版本号判断
        if len(stable_versions) == len(versions_with_metadata):
            prerelease_keywords = ['alpha', 'beta', 'rc', 'pre', 'preview', 'dev']
            stable_versions = []
            for v in versions_with_metadata:
                version = v['version'].lower()
                if not any(keyword in version for keyword in prerelease_keywords):
                    stable_versions.append(v)

        return stable_versions

    def get_domain_name(self, gem: str, **kwargs) -> str:
        return f"rubygems_{gem}"

    def get_metadata(self, gem: str, **kwargs) -> Dict:
        return {"gem": gem, "ecosystem": "Ruby/RubyGems"}
