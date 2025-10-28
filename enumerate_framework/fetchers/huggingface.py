"""Hugging Face Hub API Fetcher"""

import requests
from typing import List, Dict, Tuple
from .base import BaseFetcher


class HuggingFaceFetcher(BaseFetcher):
    """Hugging Face Hub模型、数据集、Space获取器"""

    def __init__(self, api_token: str = None):
        """
        初始化HuggingFace Fetcher

        Args:
            api_token: Hugging Face API Token (可选，用于提高速率限制)
        """
        self.api_token = api_token
        self.headers = {}
        if api_token:
            self.headers['Authorization'] = f'Bearer {api_token}'

    def fetch(self, resource_type: str = "models", **kwargs) -> Tuple[List[str], Dict, str]:
        """通用fetch方法

        Args:
            resource_type: 资源类型 ("models", "datasets", "spaces")
            **kwargs: 其他参数传递给具体的fetch方法
        """
        if resource_type == "models":
            return self.fetch_models(**kwargs)
        elif resource_type == "datasets":
            return self.fetch_datasets(**kwargs)
        elif resource_type == "spaces":
            return self.fetch_spaces(**kwargs)
        else:
            raise ValueError(f"不支持的资源类型: {resource_type}")

    def fetch_models(self, author: str = None, search: str = None,
                    filter_tag: str = None, max_items: int = 1000) -> Tuple[List[str], Dict, str]:
        """获取模型列表（简化版）

        Args:
            author: 作者/组织名称
            search: 搜索关键词
            filter_tag: 标签过滤（如 'text-generation', 'pytorch'）
            max_items: 最大获取数量
        """
        api_url = "https://huggingface.co/api/models"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {
                "author": author,
                "search": search,
                "filter": filter_tag
            },
            "authentication": "Optional (Bearer token for higher rate limits)",
            "rate_limit": "Varies based on authentication",
            "documentation": "https://huggingface.co/docs/hub/api"
        }

        models = []

        try:
            params = {}
            if author:
                params['author'] = author
            if search:
                params['search'] = search
            if filter_tag:
                params['filter'] = filter_tag
            params['limit'] = min(max_items, 1000)
            params['full'] = False  # 简化响应

            response = requests.get(api_url, params=params, headers=self.headers, timeout=15)

            if response.status_code != 200:
                print(f"  ✗ Hugging Face API错误: HTTP {response.status_code}")
                return [], api_info, ""

            data = response.json()

            for model in data[:max_items]:
                model_id = model.get('id', model.get('modelId', 'Unknown'))
                models.append(model_id)

            query_desc = []
            if author:
                query_desc.append(f"作者 '{author}'")
            if search:
                query_desc.append(f"搜索 '{search}'")
            if filter_tag:
                query_desc.append(f"标签 '{filter_tag}'")

            query_str = " 且 ".join(query_desc) if query_desc else "所有模型"
            question = f"列出Hugging Face上{query_str}的所有模型"

            return models, api_info, question

        except Exception as e:
            print(f"  ✗ Hugging Face Models API错误: {e}")
            return [], api_info, ""

    def fetch_models_with_metadata(self, author: str = None, search: str = None,
                                   filter_tag: str = None, max_items: int = 1000) -> Tuple[List[Dict], Dict, str]:
        """获取模型列表（包含完整元数据）

        Returns:
            每个model包含：
            - id: 模型ID
            - author: 作者
            - downloads: 下载次数
            - likes: 点赞数
            - tags: 标签列表
            - pipeline_tag: 主要任务类型
            - library_name: 框架（pytorch, tensorflow等）
            - last_modified: 最后更新时间
            - private: 是否私有
        """
        api_url = "https://huggingface.co/api/models"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {
                "author": author,
                "search": search,
                "filter": filter_tag
            },
            "authentication": "Optional (Bearer token for higher rate limits)",
            "rate_limit": "Varies based on authentication",
            "documentation": "https://huggingface.co/docs/hub/api",
            "metadata_fields": ["id", "author", "downloads", "likes", "tags",
                              "pipeline_tag", "library_name", "last_modified", "private"]
        }

        models = []

        try:
            params = {}
            if author:
                params['author'] = author
            if search:
                params['search'] = search
            if filter_tag:
                params['filter'] = filter_tag
            params['limit'] = min(max_items, 1000)
            params['full'] = True  # 获取完整元数据

            response = requests.get(api_url, params=params, headers=self.headers, timeout=15)

            if response.status_code != 200:
                print(f"  ✗ Hugging Face API错误: HTTP {response.status_code}")
                return [], api_info, ""

            data = response.json()

            for model in data[:max_items]:
                model_metadata = {
                    'id': model.get('id', model.get('modelId', 'Unknown')),
                    'author': model.get('author', ''),
                    'downloads': model.get('downloads', 0),
                    'likes': model.get('likes', 0),
                    'tags': model.get('tags', []),
                    'pipeline_tag': model.get('pipeline_tag', ''),
                    'library_name': model.get('library_name', ''),
                    'last_modified': model.get('lastModified', ''),
                    'private': model.get('private', False),
                    'gated': model.get('gated', False)
                }
                models.append(model_metadata)

            query_desc = []
            if author:
                query_desc.append(f"作者 '{author}'")
            if search:
                query_desc.append(f"搜索 '{search}'")
            if filter_tag:
                query_desc.append(f"标签 '{filter_tag}'")

            query_str = " 且 ".join(query_desc) if query_desc else "所有模型"
            question = f"列出Hugging Face上{query_str}的所有模型（包含完整元数据）"

            return models, api_info, question

        except Exception as e:
            print(f"  ✗ Hugging Face Models API错误: {e}")
            return [], api_info, ""

    def fetch_datasets(self, author: str = None, search: str = None,
                      filter_tag: str = None, max_items: int = 1000) -> Tuple[List[str], Dict, str]:
        """获取数据集列表（简化版）

        Args:
            author: 作者/组织名称
            search: 搜索关键词
            filter_tag: 标签过滤
            max_items: 最大获取数量
        """
        api_url = "https://huggingface.co/api/datasets"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {
                "author": author,
                "search": search,
                "filter": filter_tag
            },
            "authentication": "Optional (Bearer token for higher rate limits)",
            "rate_limit": "Varies based on authentication",
            "documentation": "https://huggingface.co/docs/hub/api"
        }

        datasets = []

        try:
            params = {}
            if author:
                params['author'] = author
            if search:
                params['search'] = search
            if filter_tag:
                params['filter'] = filter_tag
            params['limit'] = min(max_items, 1000)
            params['full'] = False

            response = requests.get(api_url, params=params, headers=self.headers, timeout=15)

            if response.status_code != 200:
                print(f"  ✗ Hugging Face API错误: HTTP {response.status_code}")
                return [], api_info, ""

            data = response.json()

            for dataset in data[:max_items]:
                dataset_id = dataset.get('id', 'Unknown')
                datasets.append(dataset_id)

            query_desc = []
            if author:
                query_desc.append(f"作者 '{author}'")
            if search:
                query_desc.append(f"搜索 '{search}'")
            if filter_tag:
                query_desc.append(f"标签 '{filter_tag}'")

            query_str = " 且 ".join(query_desc) if query_desc else "所有数据集"
            question = f"列出Hugging Face上{query_str}的所有数据集"

            return datasets, api_info, question

        except Exception as e:
            print(f"  ✗ Hugging Face Datasets API错误: {e}")
            return [], api_info, ""

    def fetch_datasets_with_metadata(self, author: str = None, search: str = None,
                                    filter_tag: str = None, max_items: int = 1000) -> Tuple[List[Dict], Dict, str]:
        """获取数据集列表（包含完整元数据）

        Returns:
            每个dataset包含：
            - id: 数据集ID
            - author: 作者
            - downloads: 下载次数
            - likes: 点赞数
            - tags: 标签列表
            - last_modified: 最后更新时间
            - private: 是否私有
        """
        api_url = "https://huggingface.co/api/datasets"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {
                "author": author,
                "search": search,
                "filter": filter_tag
            },
            "authentication": "Optional (Bearer token for higher rate limits)",
            "rate_limit": "Varies based on authentication",
            "documentation": "https://huggingface.co/docs/hub/api",
            "metadata_fields": ["id", "author", "downloads", "likes", "tags", "last_modified", "private"]
        }

        datasets = []

        try:
            params = {}
            if author:
                params['author'] = author
            if search:
                params['search'] = search
            if filter_tag:
                params['filter'] = filter_tag
            params['limit'] = min(max_items, 1000)
            params['full'] = True

            response = requests.get(api_url, params=params, headers=self.headers, timeout=15)

            if response.status_code != 200:
                print(f"  ✗ Hugging Face API错误: HTTP {response.status_code}")
                return [], api_info, ""

            data = response.json()

            for dataset in data[:max_items]:
                dataset_metadata = {
                    'id': dataset.get('id', 'Unknown'),
                    'author': dataset.get('author', ''),
                    'downloads': dataset.get('downloads', 0),
                    'likes': dataset.get('likes', 0),
                    'tags': dataset.get('tags', []),
                    'last_modified': dataset.get('lastModified', ''),
                    'private': dataset.get('private', False)
                }
                datasets.append(dataset_metadata)

            query_desc = []
            if author:
                query_desc.append(f"作者 '{author}'")
            if search:
                query_desc.append(f"搜索 '{search}'")
            if filter_tag:
                query_desc.append(f"标签 '{filter_tag}'")

            query_str = " 且 ".join(query_desc) if query_desc else "所有数据集"
            question = f"列出Hugging Face上{query_str}的所有数据集（包含完整元数据）"

            return datasets, api_info, question

        except Exception as e:
            print(f"  ✗ Hugging Face Datasets API错误: {e}")
            return [], api_info, ""

    def fetch_spaces(self, author: str = None, search: str = None,
                    max_items: int = 1000) -> Tuple[List[str], Dict, str]:
        """获取Spaces列表（简化版）

        Args:
            author: 作者/组织名称
            search: 搜索关键词
            max_items: 最大获取数量
        """
        api_url = "https://huggingface.co/api/spaces"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {
                "author": author,
                "search": search
            },
            "authentication": "Optional (Bearer token for higher rate limits)",
            "rate_limit": "Varies based on authentication",
            "documentation": "https://huggingface.co/docs/hub/api"
        }

        spaces = []

        try:
            params = {}
            if author:
                params['author'] = author
            if search:
                params['search'] = search
            params['limit'] = min(max_items, 1000)
            params['full'] = False

            response = requests.get(api_url, params=params, headers=self.headers, timeout=15)

            if response.status_code != 200:
                print(f"  ✗ Hugging Face API错误: HTTP {response.status_code}")
                return [], api_info, ""

            data = response.json()

            for space in data[:max_items]:
                space_id = space.get('id', 'Unknown')
                spaces.append(space_id)

            query_desc = []
            if author:
                query_desc.append(f"作者 '{author}'")
            if search:
                query_desc.append(f"搜索 '{search}'")

            query_str = " 且 ".join(query_desc) if query_desc else "所有Spaces"
            question = f"列出Hugging Face上{query_str}的所有Spaces"

            return spaces, api_info, question

        except Exception as e:
            print(f"  ✗ Hugging Face Spaces API错误: {e}")
            return [], api_info, ""

    # 高级过滤方法 - 模型
    def filter_by_downloads(self, models_with_metadata: List[Dict],
                           min_downloads: int) -> List[Dict]:
        """过滤下载量大于指定值的模型

        Args:
            models_with_metadata: 带元数据的模型列表
            min_downloads: 最小下载次数
        """
        return [m for m in models_with_metadata
                if m.get('downloads', 0) >= min_downloads]

    def filter_by_likes(self, items_with_metadata: List[Dict],
                       min_likes: int) -> List[Dict]:
        """过滤点赞数大于指定值的资源

        Args:
            items_with_metadata: 带元数据的资源列表
            min_likes: 最小点赞数
        """
        return [m for m in items_with_metadata
                if m.get('likes', 0) >= min_likes]

    def filter_by_task(self, models_with_metadata: List[Dict],
                      task: str) -> List[Dict]:
        """过滤特定任务类型的模型

        Args:
            models_with_metadata: 带元数据的模型列表
            task: 任务类型（如 'text-generation', 'translation', 'image-classification'）
        """
        task_lower = task.lower()
        return [m for m in models_with_metadata
                if m.get('pipeline_tag', '').lower() == task_lower]

    def filter_by_library(self, models_with_metadata: List[Dict],
                         library: str) -> List[Dict]:
        """过滤特定框架的模型

        Args:
            models_with_metadata: 带元数据的模型列表
            library: 框架名称（如 'pytorch', 'tensorflow', 'jax'）
        """
        library_lower = library.lower()
        return [m for m in models_with_metadata
                if m.get('library_name', '').lower() == library_lower]

    def filter_by_tag(self, items_with_metadata: List[Dict],
                     tag: str) -> List[Dict]:
        """过滤包含特定标签的资源

        Args:
            items_with_metadata: 带元数据的资源列表
            tag: 标签（如 'zh', 'medical', 'conversational'）
        """
        tag_lower = tag.lower()
        return [m for m in items_with_metadata
                if any(tag_lower in t.lower() for t in m.get('tags', []))]

    def filter_by_license(self, items_with_metadata: List[Dict],
                         license_pattern: str) -> List[Dict]:
        """过滤特定许可证的资源

        Args:
            items_with_metadata: 带元数据的资源列表
            license_pattern: 许可证模式（如 'apache', 'mit', 'cc'）
        """
        license_lower = license_pattern.lower()
        return [m for m in items_with_metadata
                if license_lower in str(m.get('tags', [])).lower()]

    def filter_by_update_time(self, items_with_metadata: List[Dict],
                             days_ago: int) -> List[Dict]:
        """过滤最近更新的资源

        Args:
            items_with_metadata: 带元数据的资源列表
            days_ago: 最近多少天内更新
        """
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days_ago)

        result = []
        for item in items_with_metadata:
            last_modified = item.get('last_modified', '')
            if last_modified:
                try:
                    # 解析ISO格式时间
                    modified_date = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
                    if modified_date.replace(tzinfo=None) >= cutoff_date:
                        result.append(item)
                except:
                    pass
        return result

    def get_domain_name(self, **kwargs) -> str:
        """获取域名称"""
        resource_type = kwargs.get('resource_type', 'huggingface')
        identifier = kwargs.get('identifier', '')
        if identifier:
            return f"huggingface_{resource_type}_{identifier.replace('/', '_')}"
        return f"huggingface_{resource_type}"

    def get_metadata(self, **kwargs) -> Dict:
        """获取元数据"""
        return {
            "platform": "Hugging Face Hub",
            "resource_type": kwargs.get('resource_type', 'models'),
            "identifier": kwargs.get('identifier', ''),
            "ecosystem": "AI/ML Models & Datasets"
        }
