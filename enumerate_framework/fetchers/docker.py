"""Docker Hub API Fetcher"""

import requests
from typing import List, Dict, Tuple
from .base import BaseFetcher


class DockerFetcher(BaseFetcher):
    """Docker Hub镜像tags获取器"""

    def fetch(self, image: str, limit: int = 1000) -> Tuple[List[str], Dict, str]:
        """获取Docker镜像的所有tags"""
        api_url = f"https://registry.hub.docker.com/v2/repositories/library/{image}/tags"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"page_size": 100, "page": "paginated"},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://docs.docker.com/registry/spec/api/"
        }

        tags = []
        next_url = api_url
        try:
            while next_url and len(tags) < limit:
                params = {"page_size": 100} if next_url == api_url else {}
                response = requests.get(next_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    tags.extend([tag['name'] for tag in data.get('results', [])])
                    next_url = data.get('next')  # Docker API provides next page URL
                else:
                    break
        except Exception as e:
            print(f"  ✗ Docker API错误 ({image}): {e}")

        question = f"列出Docker Hub上{image}官方镜像的所有标签"
        return tags[:limit], api_info, question

    def get_domain_name(self, image: str, **kwargs) -> str:
        return f"docker_{image}_tags"

    def get_metadata(self, image: str, **kwargs) -> Dict:
        return {"image": image, "platform": "Docker Hub"}

    def fetch_with_metadata(self, image: str, limit: int = 1000) -> Tuple[List[Dict], Dict, str]:
        """获取Docker镜像的所有tags（包含完整元数据）

        返回完整的tag元数据，包括：
        - name: 标签名称
        - last_pushed: 最后推送时间
        - last_pulled: 最后拉取时间
        - size: 镜像大小（字节）
        - architectures: 支持的架构列表
        - os_list: 支持的操作系统列表
        - images: 完整的镜像清单数组
        """
        api_url = f"https://registry.hub.docker.com/v2/repositories/library/{image}/tags"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"page_size": 100, "page": "paginated"},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://docs.docker.com/registry/spec/api/"
        }

        tags_with_metadata = []
        next_url = api_url
        try:
            while next_url and len(tags_with_metadata) < limit:
                params = {"page_size": 100} if next_url == api_url else {}
                response = requests.get(next_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for tag in data.get('results', []):
                        # 提取架构和操作系统信息
                        architectures = [img.get('architecture') for img in tag.get('images', []) if img.get('architecture')]
                        os_list = list(set(img.get('os') for img in tag.get('images', []) if img.get('os')))

                        tag_metadata = {
                            'name': tag.get('name', ''),
                            'last_pushed': tag.get('tag_last_pushed', ''),
                            'last_pulled': tag.get('tag_last_pulled', ''),
                            'size': tag.get('full_size', 0),
                            'architectures': architectures,
                            'os_list': os_list,
                            'images': tag.get('images', [])
                        }
                        tags_with_metadata.append(tag_metadata)
                    next_url = data.get('next')
                else:
                    break
        except Exception as e:
            print(f"  ✗ Docker API错误 ({image}): {e}")

        question = f"列出Docker Hub上{image}官方镜像的所有标签（含元数据）"
        return tags_with_metadata[:limit], api_info, question

    def filter_by_name_pattern(self, tags_with_metadata: List[Dict], pattern: str) -> List[Dict]:
        """根据名称模式过滤标签

        Args:
            tags_with_metadata: 包含元数据的标签列表
            pattern: 要匹配的模式字符串（不区分大小写）

        Returns:
            过滤后的标签列表

        Example:
            # 查找所有基于 alpine 的标签
            alpine_tags = fetcher.filter_by_name_pattern(tags, "alpine")
        """
        pattern_lower = pattern.lower()
        return [tag for tag in tags_with_metadata if pattern_lower in tag['name'].lower()]

    def filter_by_architecture(self, tags_with_metadata: List[Dict], arch: str) -> List[Dict]:
        """根据架构过滤标签

        Args:
            tags_with_metadata: 包含元数据的标签列表
            arch: 架构名称（如 "amd64", "arm64", "arm"等）

        Returns:
            支持指定架构的标签列表

        Example:
            # 查找所有支持 arm64 架构的标签
            arm_tags = fetcher.filter_by_architecture(tags, "arm64")
        """
        return [tag for tag in tags_with_metadata if arch in tag.get('architectures', [])]

    def sort_by_push_time(self, tags_with_metadata: List[Dict], reverse: bool = True) -> List[Dict]:
        """按推送时间排序标签

        Args:
            tags_with_metadata: 包含元数据的标签列表
            reverse: True=最新的在前（降序），False=最旧的在前（升序）

        Returns:
            排序后的标签列表

        Example:
            # 获取最近推送的标签
            recent_tags = fetcher.sort_by_push_time(tags, reverse=True)[:10]
        """
        return sorted(tags_with_metadata,
                     key=lambda t: t.get('last_pushed', ''),
                     reverse=reverse)
