"""NPM Registry API Fetcher"""

import requests
from typing import List, Dict, Tuple
from ..base import BaseFetcher


class NPMFetcher(BaseFetcher):
    """NPM包版本获取器"""

    def fetch(self, package: str) -> Tuple[List[str], Dict, str]:
        """获取NPM包的所有版本"""
        api_url = f"https://registry.npmjs.org/{package}"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md"
        }

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                versions = list(data['versions'].keys())
                question = f"列出NPM上{package}包的所有发布版本号"
                return versions, api_info, question
        except Exception as e:
            print(f"  ✗ NPM API错误 ({package}): {e}")

        return [], api_info, ""

    def fetch_with_metadata(self, package: str) -> Tuple[List[Dict], Dict, str]:
        """获取NPM包的所有版本（包含完整元数据）

        Args:
            package: NPM包名

        Returns:
            (versions_with_metadata, api_info, question)
            每个version是一个字典，包含：
            - version: 版本号
            - publish_time: 发布时间
            - maintainers: 维护者列表
            - dependencies: 依赖数量
            - deprecated: 是否被标记为废弃
        """
        api_url = f"https://registry.npmjs.org/{package}"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md",
            "metadata_fields": ["version", "publish_time", "maintainers", "dependencies", "deprecated"]
        }

        versions_with_metadata = []

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()

                versions_data = data.get('versions', {})
                time_data = data.get('time', {})

                for version, version_info in versions_data.items():
                    # 提取元数据
                    publish_time = time_data.get(version, '')
                    maintainers = version_info.get('maintainers', [])
                    dependencies = version_info.get('dependencies', {})
                    deprecated = version_info.get('deprecated', False)

                    version_metadata = {
                        "version": version,
                        "publish_time": publish_time,
                        "maintainers": [m.get('name', '') for m in maintainers] if maintainers else [],
                        "dependencies_count": len(dependencies),
                        "dependencies": dependencies,  # 添加完整依赖信息
                        "deprecated": bool(deprecated),
                        "deprecated_message": deprecated if deprecated else None
                    }

                    versions_with_metadata.append(version_metadata)

                question = f"列出NPM上{package}包的所有发布版本号"
                return versions_with_metadata, api_info, question

        except Exception as e:
            print(f"  ✗ NPM API错误 ({package}): {e}")

        return [], api_info, ""

    def filter_by_year(self, versions_with_metadata: List[Dict], year: int) -> List[Dict]:
        """过滤指定年份发布的版本

        Args:
            versions_with_metadata: 带元数据的版本列表
            year: 年份（如2023）

        Returns:
            过滤后的版本列表
        """
        return [v for v in versions_with_metadata
                if v['publish_time'] and v['publish_time'].startswith(str(year))]

    def filter_by_major_version(self, versions_with_metadata: List[Dict]) -> List[Dict]:
        """过滤major版本 (x.0.0)

        Args:
            versions_with_metadata: 带元数据的版本列表

        Returns:
            过滤后的版本列表
        """
        major_versions = []
        for v in versions_with_metadata:
            version = v['version']
            # 解析版本号，检查是否是x.0.0格式
            parts = version.split('.')
            if len(parts) >= 3:
                # 检查minor和patch都是0
                try:
                    if parts[1] == '0' and parts[2].split('-')[0] == '0':  # 处理18.0.0-rc.0这种情况
                        major_versions.append(v)
                except:
                    pass
        return major_versions

    def filter_by_deprecated(self, versions_with_metadata: List[Dict], deprecated: bool = True) -> List[Dict]:
        """过滤被标记为废弃的版本

        Args:
            versions_with_metadata: 带元数据的版本列表
            deprecated: True返回废弃的版本，False返回非废弃的版本

        Returns:
            过滤后的版本列表
        """
        return [v for v in versions_with_metadata
                if v['deprecated'] == deprecated]

    def filter_by_maintainer(self, versions_with_metadata: List[Dict], maintainer_name: str) -> List[Dict]:
        """过滤由特定维护者发布的版本

        Args:
            versions_with_metadata: 带元数据的版本列表
            maintainer_name: 维护者名称

        Returns:
            过滤后的版本列表
        """
        return [v for v in versions_with_metadata
                if maintainer_name in v.get('maintainers', [])]

    def filter_by_dependency(self, versions_with_metadata: List[Dict], dependency_name: str) -> List[Dict]:
        """过滤包含特定依赖的版本

        Note: 需要使用包含完整依赖信息的元数据

        Args:
            versions_with_metadata: 带元数据的版本列表（需要包含dependencies字段）
            dependency_name: 依赖包名称

        Returns:
            过滤后的版本列表
        """
        api_url_base = "https://registry.npmjs.org/"
        filtered_versions = []

        for v in versions_with_metadata:
            # 如果已经有dependencies信息
            if 'dependencies' in v:
                if dependency_name in v['dependencies']:
                    filtered_versions.append(v)
            # 否则需要从原始数据中获取
            else:
                # 这种情况下需要重新获取完整数据或者在fetch_with_metadata中就包含dependencies
                pass

        return filtered_versions

    def filter_prerelease_versions(self, versions_with_metadata: List[Dict]) -> List[Dict]:
        """识别预发布版本（包含alpha, beta, rc等标记）

        Args:
            versions_with_metadata: 带元数据的版本列表

        Returns:
            预发布版本列表
        """
        prerelease_keywords = ['alpha', 'beta', 'rc', 'pre', 'preview', 'dev', 'canary', 'next']

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
        prerelease_keywords = ['alpha', 'beta', 'rc', 'pre', 'preview', 'dev', 'canary', 'next']

        stable_versions = []
        for v in versions_with_metadata:
            version = v['version'].lower()
            if not any(keyword in version for keyword in prerelease_keywords):
                stable_versions.append(v)

        return stable_versions

    def get_domain_name(self, package: str) -> str:
        return f"npm_{package.replace('/', '_')}"

    def get_metadata(self, package: str) -> Dict:
        return {"package": package, "ecosystem": "JavaScript/NPM"}
