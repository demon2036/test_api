"""Go Proxy API Fetcher"""

import requests
from typing import List, Dict, Tuple
from .base import BaseFetcher


class GoProxyFetcher(BaseFetcher):
    def fetch(self, module: str) -> Tuple[List[str], Dict, str]:
        api_url = f"https://proxy.golang.org/{module}/@v/list"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://go.dev/ref/mod#goproxy-protocol"
        }
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                versions = [v for v in response.text.strip().split('\n') if v]
                question = f"列出Go module {module}的所有版本"
                return versions, api_info, question
        except Exception as e:
            print(f"  ✗ Go Proxy API错误 ({module}): {e}")
        return [], api_info, ""

    def fetch_with_metadata(self, module: str) -> Tuple[List[Dict], Dict, str]:
        """获取Go模块的所有版本（包含元数据）

        Args:
            module: Go模块名

        Returns:
            (versions_with_metadata, api_info, question)
            每个version是一个字典，包含：
            - version: 版本号
            - time: 发布时间（ISO 8601格式）
        """
        api_url = f"https://proxy.golang.org/{module}/@v/list"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://go.dev/ref/mod#goproxy-protocol",
            "metadata_fields": ["version", "time"]
        }

        versions_with_metadata = []

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                versions = [v for v in response.text.strip().split('\n') if v]

                for version in versions:
                    # 获取每个版本的.info文件来获取时间戳
                    info_url = f"https://proxy.golang.org/{module}/@v/{version}.info"
                    try:
                        info_response = requests.get(info_url, timeout=5)
                        if info_response.status_code == 200:
                            info_data = info_response.json()
                            version_metadata = {
                                "version": version,
                                "time": info_data.get('Time', '')
                            }
                        else:
                            version_metadata = {
                                "version": version,
                                "time": ""
                            }
                    except:
                        version_metadata = {
                            "version": version,
                            "time": ""
                        }

                    versions_with_metadata.append(version_metadata)

                question = f"列出Go module {module}的所有版本"
                return versions_with_metadata, api_info, question

        except Exception as e:
            print(f"  ✗ Go Proxy API错误 ({module}): {e}")

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
                if v['time'] and v['time'].startswith(str(year))]

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

    def get_domain_name(self, module: str, **kwargs) -> str:
        return f"go_{module.split('/')[-1]}"

    def get_metadata(self, module: str, **kwargs) -> Dict:
        return {"module": module, "ecosystem": "Go"}
