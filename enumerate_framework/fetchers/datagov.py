"""
Data.gov (CKAN) API Fetcher

This module provides functionality to enumerate datasets from Data.gov using the CKAN API.

Key Features:
- Enumerate all datasets from a specific organization
- Search datasets by keyword with full enumeration
- Advanced metadata filtering (format, update time, tags, etc.)
- No authentication required

Example Usage:
    fetcher = DataGovFetcher()

    # Get all datasets from NASA organization
    datasets, api_info, question = fetcher.fetch_datasets_by_org(
        organization="nasa-gov"
    )

    # Filter datasets by keyword
    mars_datasets = fetcher.filter_by_keyword(datasets, "Mars")

    # Filter by format
    csv_datasets = fetcher.filter_by_format(datasets, "CSV")
"""

import time
import requests
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
import re

from .base import BaseFetcher


class DataGovFetcher(BaseFetcher):
    """Fetcher for Data.gov datasets using CKAN API"""

    BASE_URL = "https://catalog.data.gov/api/3"

    def __init__(self):
        """Initialize the Data.gov fetcher.

        No authentication is required for Data.gov CKAN API.
        """
        pass

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a request to the CKAN API.

        Args:
            endpoint: API endpoint (e.g., 'action/package_search')
            params: Query parameters

        Returns:
            JSON response from the API

        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not data.get('success'):
                raise Exception(f"API returned success=false: {data.get('error', 'Unknown error')}")

            return data.get('result', {})

        except requests.exceptions.RequestException as e:
            raise Exception(f"Data.gov API request failed: {str(e)}")

    def _format_dataset(
        self,
        dataset: Dict,
        include_metadata: bool = False
    ) -> Any:
        """Format a dataset for output.

        Args:
            dataset: Raw dataset object from CKAN API
            include_metadata: Whether to include full metadata

        Returns:
            Formatted dataset (string ID or dict with metadata)
        """
        dataset_id = dataset.get('id', '')
        name = dataset.get('name', '')

        if not include_metadata:
            return dataset_id

        # Extract resource formats
        resources = dataset.get('resources', [])
        formats = list(set([r.get('format', 'unknown').upper() for r in resources]))

        return {
            "id": dataset_id,
            "name": name,
            "title": dataset.get('title', ''),
            "notes": dataset.get('notes', ''),
            "organization": dataset.get('organization', {}).get('name', ''),
            "organization_title": dataset.get('organization', {}).get('title', ''),
            "metadata_created": dataset.get('metadata_created', ''),
            "metadata_modified": dataset.get('metadata_modified', ''),
            "tags": [tag.get('name', '') for tag in dataset.get('tags', [])],
            "resources_count": len(resources),
            "formats": formats,
            "license_title": dataset.get('license_title', ''),
            "url": f"https://catalog.data.gov/dataset/{name}",
            "resources": resources
        }

    def fetch_datasets_by_org(
        self,
        organization: str,
        include_metadata: bool = True,
        max_items: int = 100000
    ) -> Tuple[List[Dict], Dict, str]:
        """Fetch all datasets for a specific organization.

        Args:
            organization: Organization name (e.g., 'nasa-gov', 'doc-gov')
            include_metadata: Whether to include full metadata
            max_items: Maximum number of items to return

        Returns:
            Tuple of (list of datasets, api_info dict, question string)
        """
        datasets = []
        start = 0
        rows = 1000  # CKAN's maximum

        api_url = f"{self.BASE_URL}/action/package_search"

        while len(datasets) < max_items:
            params = {
                'fq': f'organization:{organization}',
                'rows': rows,
                'start': start
            }

            result = self._make_request('action/package_search', params)

            items = result.get('results', [])
            if not items:
                break

            datasets.extend(items)

            # Check if we've reached the end
            total_count = result.get('count', 0)
            if start + len(items) >= total_count:
                break

            start += rows

        # Format datasets
        formatted = [self._format_dataset(ds, include_metadata)
                    for ds in datasets[:max_items]]

        question = f"枚举 Data.gov 上 {organization} 组织的所有数据集"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {
                "fq": f"organization:{organization}",
                "rows": rows,
                "start": "paginated"
            },
            "authentication": "None",
            "rate_limit": "No published rate limit",
            "documentation": "https://catalog.data.gov/api/3/",
            "total_found": len(datasets)
        }

        return formatted, api_info, question

    def fetch_datasets_by_query(
        self,
        query: str,
        include_metadata: bool = True,
        max_items: int = 100000
    ) -> Tuple[List[Dict], Dict, str]:
        """Search datasets by keyword query.

        Args:
            query: Search query string
            include_metadata: Whether to include full metadata
            max_items: Maximum number of items to return

        Returns:
            Tuple of (list of datasets, api_info dict, question string)
        """
        datasets = []
        start = 0
        rows = 1000

        api_url = f"{self.BASE_URL}/action/package_search"

        while len(datasets) < max_items:
            params = {
                'q': query,
                'rows': rows,
                'start': start
            }

            result = self._make_request('action/package_search', params)

            items = result.get('results', [])
            if not items:
                break

            datasets.extend(items)

            # Check if we've reached the end
            total_count = result.get('count', 0)
            if start + len(items) >= total_count:
                break

            start += rows

        # Format datasets
        formatted = [self._format_dataset(ds, include_metadata)
                    for ds in datasets[:max_items]]

        question = f"枚举 Data.gov 上与 '{query}' 相关的所有数据集"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {
                "q": query,
                "rows": rows,
                "start": "paginated"
            },
            "authentication": "None",
            "rate_limit": "No published rate limit",
            "documentation": "https://catalog.data.gov/api/3/",
            "total_found": len(datasets)
        }

        return formatted, api_info, question

    # Advanced filter methods

    def filter_by_keyword(
        self,
        datasets: List[Dict],
        keyword: str,
        search_fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """Filter datasets by keyword in title, notes, or tags.

        This answers the advanced question:
        "List all datasets from the 'NASA' organization related to 'Mars'."

        Args:
            datasets: List of datasets with metadata
            keyword: Keyword to search for (case-insensitive)
            search_fields: Fields to search in. Defaults to ['title', 'notes', 'tags']

        Returns:
            Filtered list of datasets
        """
        if search_fields is None:
            search_fields = ['title', 'notes', 'tags']

        keyword_lower = keyword.lower()
        filtered = []

        for dataset in datasets:
            match = False

            if 'title' in search_fields:
                if keyword_lower in dataset.get('title', '').lower():
                    match = True

            if 'notes' in search_fields and not match:
                if keyword_lower in dataset.get('notes', '').lower():
                    match = True

            if 'tags' in search_fields and not match:
                tags = dataset.get('tags', [])
                for tag in tags:
                    if keyword_lower in tag.lower():
                        match = True
                        break

            if match:
                filtered.append(dataset)

        return filtered

    def filter_by_format(
        self,
        datasets: List[Dict],
        format_type: str
    ) -> List[Dict]:
        """Filter datasets by resource format.

        This answers the advanced question:
        "Find all CSV datasets related to 'air quality'."
        "Enumerate all datasets from the 'Department of Commerce' that are available in GeoJSON format."

        Args:
            datasets: List of datasets with metadata
            format_type: Format to filter by (e.g., 'CSV', 'JSON', 'GeoJSON', 'XML', 'PDF')

        Returns:
            Datasets that have at least one resource in the specified format
        """
        format_upper = format_type.upper()

        return [
            dataset for dataset in datasets
            if format_upper in dataset.get('formats', [])
        ]

    def filter_by_update_time(
        self,
        datasets: List[Dict],
        days_ago: int
    ) -> List[Dict]:
        """Filter datasets updated within the last N days.

        This answers the advanced question:
        "Find all CSV datasets related to 'air quality' updated in the last month."

        Args:
            datasets: List of datasets with metadata
            days_ago: Number of days to look back

        Returns:
            Datasets updated within the specified time period
        """
        cutoff_date = datetime.now() - timedelta(days=days_ago)

        results = []
        for dataset in datasets:
            modified_str = dataset.get('metadata_modified')
            if modified_str:
                try:
                    # Parse ISO format timestamp
                    modified = datetime.fromisoformat(
                        modified_str.replace('Z', '+00:00')
                    )
                    # Make naive for comparison
                    modified = modified.replace(tzinfo=None)

                    if modified >= cutoff_date:
                        results.append(dataset)
                except (ValueError, AttributeError):
                    # Skip datasets with invalid timestamps
                    continue

        return results

    def filter_by_license(
        self,
        datasets: List[Dict],
        license_pattern: str
    ) -> List[Dict]:
        """Filter datasets by license type.

        Args:
            datasets: List of datasets with metadata
            license_pattern: License pattern to match (case-insensitive regex)

        Returns:
            Datasets with matching license
        """
        regex = re.compile(license_pattern, re.IGNORECASE)

        return [
            dataset for dataset in datasets
            if regex.search(dataset.get('license_title', ''))
        ]

    def filter_by_organization(
        self,
        datasets: List[Dict],
        organization_pattern: str
    ) -> List[Dict]:
        """Filter datasets by organization name.

        Args:
            datasets: List of datasets with metadata
            organization_pattern: Organization pattern to match (case-insensitive regex)

        Returns:
            Datasets from matching organizations
        """
        regex = re.compile(organization_pattern, re.IGNORECASE)

        return [
            dataset for dataset in datasets
            if regex.search(dataset.get('organization', ''))
            or regex.search(dataset.get('organization_title', ''))
        ]

    def filter_by_tag(
        self,
        datasets: List[Dict],
        tag: str
    ) -> List[Dict]:
        """Filter datasets by specific tag.

        Args:
            datasets: List of datasets with metadata
            tag: Tag to filter by (case-insensitive)

        Returns:
            Datasets with the specified tag
        """
        tag_lower = tag.lower()

        return [
            dataset for dataset in datasets
            if any(tag_lower == t.lower() for t in dataset.get('tags', []))
        ]

    def filter_by_resource_count(
        self,
        datasets: List[Dict],
        min_count: Optional[int] = None,
        max_count: Optional[int] = None
    ) -> List[Dict]:
        """Filter datasets by number of resources.

        Args:
            datasets: List of datasets with metadata
            min_count: Minimum number of resources
            max_count: Maximum number of resources

        Returns:
            Datasets with resource count in the specified range
        """
        filtered = []
        for dataset in datasets:
            count = dataset.get('resources_count', 0)

            if min_count is not None and count < min_count:
                continue
            if max_count is not None and count > max_count:
                continue

            filtered.append(dataset)

        return filtered

    def get_unique_formats(
        self,
        datasets: List[Dict]
    ) -> List[str]:
        """Get all unique data formats across all datasets.

        Args:
            datasets: List of datasets with metadata

        Returns:
            Sorted list of unique formats
        """
        formats = set()
        for dataset in datasets:
            formats.update(dataset.get('formats', []))

        return sorted(list(formats))

    def get_unique_organizations(
        self,
        datasets: List[Dict]
    ) -> List[str]:
        """Get all unique organizations across all datasets.

        Args:
            datasets: List of datasets with metadata

        Returns:
            Sorted list of unique organizations
        """
        orgs = set()
        for dataset in datasets:
            org = dataset.get('organization_title')
            if org:
                orgs.add(org)

        return sorted(list(orgs))

    def get_dataset_stats(
        self,
        datasets: List[Dict]
    ) -> Dict:
        """Get statistics about a collection of datasets.

        Args:
            datasets: List of datasets with metadata

        Returns:
            Dictionary with statistics
        """
        if not datasets:
            return {
                "total_datasets": 0,
                "total_resources": 0,
                "unique_formats": [],
                "unique_organizations": [],
                "avg_resources_per_dataset": 0
            }

        total_resources = sum(ds.get('resources_count', 0) for ds in datasets)
        formats = self.get_unique_formats(datasets)
        orgs = self.get_unique_organizations(datasets)

        return {
            "total_datasets": len(datasets),
            "total_resources": total_resources,
            "unique_formats": formats,
            "unique_organizations": orgs,
            "avg_resources_per_dataset": total_resources / len(datasets)
        }

    # Implement abstract methods

    def fetch(
        self,
        organization: Optional[str] = None,
        query: Optional[str] = None,
        **kwargs
    ) -> Tuple[List, Dict, str]:
        """Fetch datasets (generic method).

        Args:
            organization: Organization name to filter by
            query: Search query string
            **kwargs: Additional parameters

        Returns:
            Tuple of (list of dataset IDs, api_info dict, question string)
        """
        if organization:
            datasets, api_info, question = self.fetch_datasets_by_org(
                organization,
                include_metadata=False
            )
            return datasets, api_info, question

        if query:
            datasets, api_info, question = self.fetch_datasets_by_query(
                query,
                include_metadata=False
            )
            return datasets, api_info, question

        return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        """Return domain name for file naming.

        Args:
            **kwargs: Query parameters

        Returns:
            Domain name string for file naming
        """
        org = kwargs.get('organization')
        if org:
            return f"datagov_{org}"

        query = kwargs.get('query')
        if query:
            # Clean query for filename
            clean_query = re.sub(r'[^\w\s-]', '', query).strip().replace(' ', '_')
            return f"datagov_query_{clean_query}"

        return "datagov"

    def get_metadata(self, **kwargs) -> Dict:
        """Return metadata about the query.

        Args:
            **kwargs: Query parameters

        Returns:
            Metadata dictionary
        """
        metadata = {
            "api": "Data.gov CKAN API",
            "requires_auth": False
        }

        if 'organization' in kwargs:
            metadata['organization'] = kwargs['organization']

        if 'query' in kwargs:
            metadata['query'] = kwargs['query']

        return metadata
