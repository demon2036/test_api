"""Conda API Fetcher"""

import requests
from typing import List, Dict, Tuple
from .base import BaseFetcher


class CondaFetcher(BaseFetcher):
    def fetch(self, package: str, channel: str = "conda-forge") -> Tuple[List[str], Dict, str]:
        api_url = f"https://api.anaconda.org/package/{channel}/{package}"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://docs.anaconda.com/anaconda-cloud/api/"
        }
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                versions = sorted(list(set([f['version'] for f in data.get('files', [])])))
                question = f"列出Conda {channel}频道上{package}的所有版本"
                return versions, api_info, question
        except Exception as e:
            print(f"  ✗ Conda API错误 ({package}): {e}")
        return [], api_info, ""

    def fetch_with_metadata(self, package: str, channel: str = "conda-forge") -> Tuple[List[Dict], Dict, str]:
        """获取Conda包的所有版本（包含元数据）

        Args:
            package: Conda包名
            channel: Conda频道（默认为conda-forge）

        Returns:
            (versions_with_metadata, api_info, question)
            每个version是一个字典，包含：
            - version: 版本号
            - upload_time: 最早上传时间
            - total_downloads: 该版本所有文件的总下载量
            - file_count: 文件数量（不同平台/Python版本）
            - platforms: 支持的平台列表
        """
        api_url = f"https://api.anaconda.org/package/{channel}/{package}"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://docs.anaconda.com/anaconda-cloud/api/",
            "metadata_fields": ["version", "upload_time", "total_downloads", "file_count", "platforms"]
        }

        versions_with_metadata = []

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                files = data.get('files', [])

                # 按版本分组文件
                version_files = {}
                for file in files:
                    version = file.get('version', '')
                    if version not in version_files:
                        version_files[version] = []
                    version_files[version].append(file)

                # 为每个版本聚合元数据
                for version, files_list in sorted(version_files.items()):
                    # 获取最早的上传时间
                    upload_times = [f.get('upload_time', '') for f in files_list if f.get('upload_time')]
                    earliest_upload = min(upload_times) if upload_times else ''

                    # 计算总下载量
                    total_downloads = sum(f.get('ndownloads', 0) for f in files_list)

                    # 获取支持的平台
                    platforms = list(set(
                        f.get('attrs', {}).get('platform', 'unknown')
                        for f in files_list
                        if f.get('attrs', {}).get('platform')
                    ))

                    version_metadata = {
                        "version": version,
                        "upload_time": earliest_upload,
                        "total_downloads": total_downloads,
                        "file_count": len(files_list),
                        "platforms": platforms
                    }
                    versions_with_metadata.append(version_metadata)

                question = f"列出Conda {channel}频道上{package}的所有版本"
                return versions_with_metadata, api_info, question

        except Exception as e:
            print(f"  ✗ Conda API错误 ({package}): {e}")

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
                if v['upload_time'] and str(year) in v['upload_time']]

    def filter_by_platform(self, versions_with_metadata: List[Dict], platform: str) -> List[Dict]:
        """过滤支持特定平台的版本

        Args:
            versions_with_metadata: 带元数据的版本列表
            platform: 平台名称（如'linux', 'osx', 'win'）

        Returns:
            过滤后的版本列表
        """
        return [v for v in versions_with_metadata
                if any(platform in p for p in v.get('platforms', []))]

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
        return f"conda_{package}"

    def get_metadata(self, package: str, channel: str = "conda-forge", **kwargs) -> Dict:
        return {"package": package, "channel": channel, "ecosystem": "Python/Conda"}
