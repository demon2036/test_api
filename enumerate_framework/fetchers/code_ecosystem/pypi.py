"""PyPI API Fetcher"""

import requests
from typing import List, Dict, Tuple
from ..base import BaseFetcher


class PyPIFetcher(BaseFetcher):
    """PyPI包版本获取器"""

    def fetch(self, package: str) -> Tuple[List[str], Dict, str]:
        """获取PyPI包的所有版本"""
        api_url = f"https://pypi.org/pypi/{package}/json"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://warehouse.pypa.io/api-reference/json.html"
        }

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                versions = list(data['releases'].keys())
                question = f"列出Python {package}库在PyPI上的所有发布版本号"
                return versions, api_info, question
        except Exception as e:
            print(f"  ✗ PyPI API错误 ({package}): {e}")

        return [], api_info, ""

    def fetch_with_metadata(self, package: str) -> Tuple[List[Dict], Dict, str]:
        """获取PyPI包的所有版本（包含完整元数据）

        Args:
            package: PyPI包名

        Returns:
            (versions_with_metadata, api_info, question)
            每个version是一个字典，包含：
            - version: 版本号
            - upload_time: 上传时间
            - python_version: Python版本要求
            - has_wheel: 是否有wheel文件
            - has_sdist: 是否有源码发布
            - yanked: 是否被撤回
        """
        api_url = f"https://pypi.org/pypi/{package}/json"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://warehouse.pypa.io/api-reference/json.html",
            "metadata_fields": ["version", "upload_time", "python_version", "has_wheel", "has_sdist", "yanked"]
        }

        versions_with_metadata = []

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                releases = data.get('releases', {})

                for version, files in releases.items():
                    if not files:  # 有些版本可能没有文件
                        continue

                    # 从文件中提取元数据（取第一个文件的时间作为版本发布时间）
                    first_file = files[0] if files else {}
                    upload_time = first_file.get('upload_time', '')

                    # 检查是否有wheel和sdist
                    has_wheel = any(f.get('packagetype') == 'bdist_wheel' for f in files)
                    has_sdist = any(f.get('packagetype') == 'sdist' for f in files)

                    # 获取Python版本要求（从第一个文件）
                    python_version = first_file.get('python_version', 'source')

                    # 检查是否被撤回
                    yanked = first_file.get('yanked', False)

                    version_metadata = {
                        "version": version,
                        "upload_time": upload_time,
                        "python_version": python_version,
                        "has_wheel": has_wheel,
                        "has_sdist": has_sdist,
                        "yanked": yanked,
                        "file_count": len(files)
                    }

                    versions_with_metadata.append(version_metadata)

                question = f"列出Python {package}库在PyPI上的所有发布版本号"
                return versions_with_metadata, api_info, question

        except Exception as e:
            print(f"  ✗ PyPI API错误 ({package}): {e}")

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
                if v['upload_time'] and v['upload_time'].startswith(str(year))]

    def filter_by_wheel(self, versions_with_metadata: List[Dict], has_wheel: bool = True) -> List[Dict]:
        """过滤包含wheel文件的版本

        Args:
            versions_with_metadata: 带元数据的版本列表
            has_wheel: True返回有wheel的版本，False返回没有wheel的版本

        Returns:
            过滤后的版本列表
        """
        return [v for v in versions_with_metadata
                if v['has_wheel'] == has_wheel]

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
        """识别预发布版本（包含a, b, rc, dev, pre等标记）

        Args:
            versions_with_metadata: 带元数据的版本列表

        Returns:
            预发布版本列表
        """
        # PEP 440 预发布版本标识
        prerelease_keywords = ['a', 'b', 'rc', 'alpha', 'beta', 'dev', 'pre', 'preview']

        prerelease_versions = []
        for v in versions_with_metadata:
            version = v['version'].lower()
            # 检查是否包含预发布标记
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
        prerelease_keywords = ['a', 'b', 'rc', 'alpha', 'beta', 'dev', 'pre', 'preview']

        stable_versions = []
        for v in versions_with_metadata:
            version = v['version'].lower()
            if not any(keyword in version for keyword in prerelease_keywords):
                stable_versions.append(v)

        return stable_versions

    def filter_by_python_version(self, versions_with_metadata: List[Dict], python_version: str) -> List[Dict]:
        """过滤支持特定Python版本的版本

        Args:
            versions_with_metadata: 带元数据的版本列表
            python_version: Python版本（如'3.9', 'py3', 'source'）

        Returns:
            过滤后的版本列表
        """
        return [v for v in versions_with_metadata
                if python_version in v.get('python_version', '')]

    def get_domain_name(self, package: str) -> str:
        return f"pypi_{package}"

    def get_metadata(self, package: str) -> Dict:
        return {"package": package, "ecosystem": "Python/PyPI"}
