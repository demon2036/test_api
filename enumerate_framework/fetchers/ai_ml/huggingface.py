"""Hugging Face Hub API Fetcher - Streamlined Version"""

import requests
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from ..base import BaseFetcher


class HuggingFaceFetcher(BaseFetcher):
    """Hugging Face Hub fetcher for models, datasets, and spaces"""

    BASE_URL = "https://huggingface.co/api"
    RESOURCE_TYPES = {"models", "datasets", "spaces"}
    QUESTION_TYPES = {
        "basic": "basic_enumeration",
        "advanced": "advanced_query"
    }

    def __init__(self, api_token: Optional[str] = None):
        """Initialize Hugging Face fetcher

        Args:
            api_token: Optional API token for higher rate limits
        """
        self.api_token = api_token
        self.headers = {'Authorization': f'Bearer {api_token}'} if api_token else {}

    def _paginate(self, url: str, params: Dict, max_items: int,
                  extract_fn=None) -> List:
        """Generic pagination handler for all resource types

        Args:
            url: API endpoint URL
            params: Query parameters
            max_items: Maximum items to fetch
            extract_fn: Optional function to extract data from response items

        Returns:
            List of items (IDs or metadata dicts)
        """
        items = []
        current_url = url
        first_request = True

        while current_url and len(items) < max_items:
            response = requests.get(
                current_url,
                params=params if first_request else {},
                headers=self.headers,
                timeout=15
            )
            first_request = False

            if response.status_code != 200:
                print(f"  ✗ API Error: HTTP {response.status_code}")
                break

            data = response.json()
            for item in data:
                if len(items) >= max_items:
                    break
                items.append(extract_fn(item) if extract_fn else item)

            # Check for pagination
            next_link = response.links.get('next')
            current_url = next_link['url'] if next_link else None

        return items

    def _build_query_string(self, author: Optional[str] = None,
                           search: Optional[str] = None,
                           filter_tag: Optional[str] = None,
                           resource_type: str = "models") -> str:
        """Build query description string for question generation"""
        parts = []
        if author:
            parts.append(f"作者 '{author}'")
        if search:
            parts.append(f"搜索 '{search}'")
        if filter_tag:
            parts.append(f"标签 '{filter_tag}'")

        resource_names = {
            "models": "模型",
            "datasets": "数据集",
            "spaces": "Spaces"
        }
        query_str = " 且 ".join(parts) if parts else f"所有{resource_names[resource_type]}"
        return f"列出 Hugging Face Hub 上{query_str}的所有{resource_names[resource_type]}"

    def build_advanced_question(
        self,
        resource_type: str,
        sort: str,
        limit: int,
        direction: int = -1,
        filter_tag: Optional[str] = None,
        search: Optional[str] = None,
        secondary_filters: Optional[Dict[str, str]] = None
    ) -> str:
        """构建高级查询问题描述，强调 Hugging Face Hub 来源"""
        resource_names = {
            "models": "模型",
            "datasets": "数据集",
            "spaces": "Spaces"
        }
        resource_name = resource_names.get(resource_type, resource_type)

        sort_labels = {
            "downloads": "下载量",
            "likes": "点赞数",
            "lastModified": "最近更新"
        }
        sort_label = sort_labels.get(sort, sort)

        qualifiers: List[str] = []
        if filter_tag:
            qualifiers.append(f"带有“{filter_tag}”标签")
        if search:
            qualifiers.append(f"与“{search}”相关")

        if secondary_filters:
            secondary_mapping = {
                "library": lambda value: f"使用“{value}”库",
                "tag": lambda value: f"包含“{value}”标签"
            }
            for key, value in secondary_filters.items():
                formatter = secondary_mapping.get(key)
                if formatter and value:
                    qualifiers.append(formatter(value))

        qualifier_text = "、".join(qualifiers)
        if qualifier_text:
            qualifier_text = f"{qualifier_text}的"

        if sort == "lastModified":
            sort_phrase = "最近更新的"
        else:
            if direction == -1:
                sort_phrase = f"{sort_label}最高的"
            else:
                sort_phrase = f"{sort_label}最低的"

        limit_text = f"{limit}个" if limit else "指定数量的"

        return f"在 Hugging Face Hub 上列出{qualifier_text}{resource_name}中{sort_phrase}{limit_text}"

    def fetch(self, resource_type: str = "models", **kwargs) -> Tuple[List[str], Dict, str]:
        """Generic fetch method for all resource types

        Args:
            resource_type: Resource type ("models", "datasets", "spaces")
            **kwargs: Additional parameters (author, search, filter_tag, max_items, full)
        """
        if resource_type == "models":
            return self.fetch_models(**kwargs)
        elif resource_type == "datasets":
            return self.fetch_datasets(**kwargs)
        elif resource_type == "spaces":
            return self.fetch_spaces(**kwargs)
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def _fetch_resource(self, resource_type: str, author: Optional[str] = None,
                       search: Optional[str] = None, filter_tag: Optional[str] = None,
                       max_items: int = 1000, full: bool = False,
                       sort: Optional[str] = None, direction: int = -1) -> Tuple[List, Dict, str]:
        """Unified method to fetch any resource type (models, datasets, spaces)

        Args:
            resource_type: Type of resource to fetch
            author: Author/organization name
            search: Search keywords
            filter_tag: Tag filter (only for models/datasets)
            max_items: Maximum items to fetch
            full: Whether to include full metadata
            sort: Sort property ('downloads', 'likes', 'author', etc.)
            direction: Sort direction (-1 for descending, 1 for ascending)

        Returns:
            Tuple of (items, api_info, question)
        """
        api_url = f"{self.BASE_URL}/{resource_type}"
        params = {'limit': min(max_items, 1000), 'full': full}
        if author:
            params['author'] = author
        if search:
            params['search'] = search
        if filter_tag and resource_type in ['models', 'datasets']:
            params['filter'] = filter_tag
        if sort:
            params['sort'] = sort
            params['direction'] = direction

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {k: v for k, v in [("author", author), ("search", search),
                                            ("filter", filter_tag), ("sort", sort),
                                            ("direction", direction if sort else None)] if v is not None},
            "authentication": "Optional (Bearer token for higher rate limits)",
            "rate_limit": "Varies based on authentication",
            "documentation": "https://huggingface.co/docs/hub/api"
        }

        if full:
            api_info["metadata_fields"] = self._get_metadata_fields(resource_type)

        try:
            # Define extraction function based on whether we want full metadata
            if full:
                extract_fn = lambda item: self._extract_metadata(item, resource_type)
            else:
                extract_fn = lambda item: item.get('id', item.get('modelId', 'Unknown'))

            items = self._paginate(api_url, params, max_items, extract_fn)
            question = self._build_query_string(author, search, filter_tag, resource_type)
            if full:
                question += "（包含完整元数据）"

            return items, api_info, question

        except Exception as e:
            print(f"  ✗ Hugging Face {resource_type.title()} API错误: {e}")
            return [], api_info, ""

    def _get_metadata_fields(self, resource_type: str) -> List[str]:
        """Get metadata fields for a resource type"""
        common = ["id", "author", "downloads", "likes", "tags", "last_modified", "private"]
        if resource_type == "models":
            return common + ["pipeline_tag", "library_name", "gated"]
        return common

    def _extract_metadata(self, item: Dict, resource_type: str) -> Dict:
        """Extract metadata from API response item"""
        metadata = {
            'id': item.get('id', item.get('modelId', 'Unknown')),
            'author': item.get('author', ''),
            'downloads': item.get('downloads', 0),
            'likes': item.get('likes', 0),
            'tags': item.get('tags', []),
            'last_modified': item.get('lastModified', ''),
            'private': item.get('private', False)
        }
        if resource_type == "models":
            metadata.update({
                'pipeline_tag': item.get('pipeline_tag', ''),
                'library_name': item.get('library_name', ''),
                'gated': item.get('gated', False)
            })
        return metadata

    def fetch_models(self, author: Optional[str] = None, search: Optional[str] = None,
                    filter_tag: Optional[str] = None, max_items: int = 1000,
                    sort: Optional[str] = None, direction: int = -1) -> Tuple[List[str], Dict, str]:
        """Fetch model list (simplified - IDs only)"""
        return self._fetch_resource("models", author, search, filter_tag, max_items, full=False, sort=sort, direction=direction)

    def fetch_models_with_metadata(self, author: Optional[str] = None, search: Optional[str] = None,
                                   filter_tag: Optional[str] = None, max_items: int = 1000,
                                   sort: Optional[str] = None, direction: int = -1) -> Tuple[List[Dict], Dict, str]:
        """Fetch model list with full metadata

        Args:
            author: Filter by author/organization
            search: Search keywords
            filter_tag: Filter by tag (e.g., 'text-generation', 'pytorch')
            max_items: Maximum number of items to fetch
            sort: Sort by field ('downloads', 'likes', 'author', etc.)
            direction: Sort direction (-1 for descending, 1 for ascending)
        """
        return self._fetch_resource("models", author, search, filter_tag, max_items, full=True, sort=sort, direction=direction)

    def fetch_datasets(self, author: Optional[str] = None, search: Optional[str] = None,
                      filter_tag: Optional[str] = None, max_items: int = 1000,
                      sort: Optional[str] = None, direction: int = -1) -> Tuple[List[str], Dict, str]:
        """Fetch dataset list (simplified - IDs only)"""
        return self._fetch_resource("datasets", author, search, filter_tag, max_items, full=False, sort=sort, direction=direction)

    def fetch_datasets_with_metadata(self, author: Optional[str] = None, search: Optional[str] = None,
                                    filter_tag: Optional[str] = None, max_items: int = 1000,
                                    sort: Optional[str] = None, direction: int = -1) -> Tuple[List[Dict], Dict, str]:
        """Fetch dataset list with full metadata

        Args:
            author: Filter by author/organization
            search: Search keywords
            filter_tag: Filter by tag
            max_items: Maximum number of items to fetch
            sort: Sort by field ('downloads', 'likes', etc.)
            direction: Sort direction (-1 for descending, 1 for ascending)
        """
        return self._fetch_resource("datasets", author, search, filter_tag, max_items, full=True, sort=sort, direction=direction)

    def fetch_spaces(self, author: Optional[str] = None, search: Optional[str] = None,
                    max_items: int = 1000, sort: Optional[str] = None, direction: int = -1) -> Tuple[List[str], Dict, str]:
        """Fetch spaces list (simplified - IDs only)"""
        return self._fetch_resource("spaces", author, search, None, max_items, full=False, sort=sort, direction=direction)

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
                if (m.get('library_name', '').lower() == library_lower or
                    any(library_lower in tag.lower() for tag in m.get('tags', [])))]

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
        cutoff_date = datetime.now() - timedelta(days=days_ago)

        def is_recent(item):
            last_modified = item.get('last_modified', '')
            if not last_modified:
                return False
            try:
                modified_date = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
                return modified_date.replace(tzinfo=None) >= cutoff_date
            except:
                return False

        return [item for item in items_with_metadata if is_recent(item)]

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
