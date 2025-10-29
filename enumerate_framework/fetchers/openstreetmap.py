"""
OpenStreetMap Overpass API Fetcher

This module provides functionality to enumerate map features (nodes, ways, relations)
from OpenStreetMap using the Overpass API.

Key Features:
- Enumerate all features within a bounding box by tags
- Radius-based queries (e.g., "all hospitals within 5km")
- Advanced metadata filtering (playgrounds, subway connections, etc.)
- No authentication required

Example Usage:
    fetcher = OpenStreetMapFetcher()

    # Find all hospitals in Manhattan
    bbox = (40.7000, -74.0200, 40.8000, -73.9000)
    items, api_info, question = fetcher.fetch_with_metadata(
        bbox=bbox,
        tags={"amenity": "hospital"}
    )

    # Find parks with playgrounds
    parks = fetcher.filter_with_playground(items)
"""

import time
import requests
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
import re
import math

from .base import BaseFetcher


class OpenStreetMapFetcher(BaseFetcher):
    """Fetcher for OpenStreetMap data using Overpass API"""

    BASE_URL = "https://overpass-api.de/api/interpreter"

    def __init__(self):
        """Initialize the OpenStreetMap fetcher.

        No authentication is required for Overpass API.
        """
        pass

    def _build_overpass_query(
        self,
        element_types: List[str],
        tags: Dict[str, str],
        bbox: Optional[Tuple[float, float, float, float]] = None,
        timeout: int = 300
    ) -> str:
        """Build an Overpass QL query.

        Args:
            element_types: List of element types to query ('node', 'way', 'relation')
            tags: Dictionary of OSM tags to filter by (e.g., {'amenity': 'hospital'})
            bbox: Optional bounding box as (min_lat, min_lon, max_lat, max_lon)
            timeout: Query timeout in seconds

        Returns:
            Overpass QL query string
        """
        # Build tag filter string
        tag_filters = ''.join([f'["{k}"="{v}"]' for k, v in tags.items()])

        # Build bbox string
        bbox_str = f"({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})" if bbox else ""

        # Build query for each element type
        elements = []
        for elem_type in element_types:
            elements.append(f'  {elem_type}{tag_filters}{bbox_str};')

        query = f"""[out:json][timeout:{timeout}];
(
{chr(10).join(elements)}
);
out body;
>;
out skel qt;"""

        return query

    def _build_radius_query(
        self,
        lat: float,
        lon: float,
        radius_m: int,
        element_types: List[str],
        tags: Dict[str, str],
        timeout: int = 300
    ) -> str:
        """Build an Overpass QL query for radius-based search.

        Args:
            lat: Latitude of center point
            lon: Longitude of center point
            radius_m: Radius in meters
            element_types: List of element types to query
            tags: Dictionary of OSM tags to filter by
            timeout: Query timeout in seconds

        Returns:
            Overpass QL query string
        """
        tag_filters = ''.join([f'["{k}"="{v}"]' for k, v in tags.items()])

        elements = []
        for elem_type in element_types:
            elements.append(f'  {elem_type}{tag_filters}(around:{radius_m},{lat},{lon});')

        query = f"""[out:json][timeout:{timeout}];
(
{chr(10).join(elements)}
);
out body;
>;
out skel qt;"""

        return query

    def _execute_query(self, query: str) -> Dict[str, Any]:
        """Execute an Overpass query and return the response.

        Args:
            query: Overpass QL query string

        Returns:
            JSON response from Overpass API

        Raises:
            requests.RequestException: If the API request fails
        """
        try:
            response = requests.post(
                self.BASE_URL,
                data={"data": query},
                timeout=330  # Slightly longer than query timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Overpass API request failed: {str(e)}")

    def _calculate_centroid(
        self,
        element: Dict,
        node_lookup: Optional[Dict[int, Tuple[float, float]]] = None
    ) -> Tuple[Optional[float], Optional[float]]:
        """Calculate centroid for ways and relations.

        Args:
            element: OSM element dictionary
            node_lookup: Optional mapping of node id -> (lat, lon)

        Returns:
            Tuple of (lat, lon)
        """
        if element['type'] == 'node':
            return (element.get('lat'), element.get('lon'))

        # For ways/relations, calculate centroid from node references
        if 'center' in element:
            return (element['center']['lat'], element['center']['lon'])

        if node_lookup and element['type'] == 'way':
            node_coords = [
                node_lookup.get(node_id)
                for node_id in element.get('nodes', [])
                if node_lookup.get(node_id) is not None
            ]
            if node_coords:
                lat = sum(coord[0] for coord in node_coords) / len(node_coords)
                lon = sum(coord[1] for coord in node_coords) / len(node_coords)
                return (lat, lon)

        if node_lookup and element['type'] == 'relation':
            node_coords = []
            for member in element.get('members', []):
                if member.get('type') == 'node':
                    coord = node_lookup.get(member.get('ref'))
                    if coord:
                        node_coords.append(coord)
            if node_coords:
                lat = sum(coord[0] for coord in node_coords) / len(node_coords)
                lon = sum(coord[1] for coord in node_coords) / len(node_coords)
                return (lat, lon)

        # Fallback: return None if no coordinates available
        return (None, None)

    def _format_element(
        self,
        element: Dict,
        include_metadata: bool = False,
        node_lookup: Optional[Dict[int, Tuple[float, float]]] = None
    ) -> Any:
        """Format an OSM element for output.

        Args:
            element: Raw OSM element from Overpass API
            include_metadata: Whether to include full metadata
            node_lookup: Optional mapping of node id -> (lat, lon)

        Returns:
            Formatted element (string ID or dict with metadata)
        """
        element_id = f"{element['type']}/{element['id']}"

        if not include_metadata:
            return element_id

        lat, lon = self._calculate_centroid(element, node_lookup)

        return {
            "id": element_id,
            "type": element['type'],
            "lat": lat,
            "lon": lon,
            "tags": element.get('tags', {}),
            "version": element.get('version'),
            "changeset": element.get('changeset'),
            "timestamp": element.get('timestamp'),
            "user": element.get('user')
        }

    def fetch(
        self,
        bbox: Tuple[float, float, float, float],
        tags: Dict[str, str],
        element_types: Optional[List[str]] = None,
        max_items: int = 10000
    ) -> Tuple[List[str], Dict, str]:
        """Fetch OSM elements within a bounding box (IDs only).

        Args:
            bbox: Bounding box as (min_lat, min_lon, max_lat, max_lon)
            tags: Dictionary of OSM tags to filter by
            element_types: List of element types ('node', 'way', 'relation').
                          Defaults to ['node', 'way', 'relation']
            max_items: Maximum number of items to return

        Returns:
            Tuple of (list of element IDs, api_info dict, question string)
        """
        if element_types is None:
            element_types = ['node', 'way', 'relation']

        # Build and execute query
        query = self._build_overpass_query(element_types, tags, bbox)

        response = self._execute_query(query)

        # Extract elements
        elements = response.get('elements', [])

        node_lookup = {
            elem['id']: (elem.get('lat'), elem.get('lon'))
            for elem in elements
            if elem.get('type') == 'node'
            and elem.get('lat') is not None
            and elem.get('lon') is not None
        }

        # Filter out node references (nodes that are part of ways)
        # We only want the actual features, not the geometry nodes
        main_elements = [
            elem for elem in elements
            if 'tags' in elem  # Elements with tags are actual features
        ]

        # Format as IDs only
        items = [self._format_element(elem, include_metadata=False, node_lookup=node_lookup)
                for elem in main_elements[:max_items]]

        # Build tag description
        tag_desc = ', '.join([f'{k}={v}' for k, v in tags.items()])

        question = (
            f"枚举边界框 {bbox} 内所有标签为 {tag_desc} 的地图要素"
        )

        api_info = {
            "api_endpoint": self.BASE_URL,
            "method": "POST",
            "parameters": {
                "query": query[:200] + "..." if len(query) > 200 else query,
                "bbox": bbox,
                "tags": tags,
                "element_types": element_types
            },
            "authentication": "None",
            "rate_limit": "Fair use policy (no hard limit, ~1 query/second recommended)",
            "documentation": "https://wiki.openstreetmap.org/wiki/Overpass_API"
        }

        return items, api_info, question

    def fetch_with_metadata(
        self,
        bbox: Tuple[float, float, float, float],
        tags: Dict[str, str],
        element_types: Optional[List[str]] = None,
        max_items: int = 10000
    ) -> Tuple[List[Dict], Dict, str]:
        """Fetch OSM elements within a bounding box with full metadata.

        Args:
            bbox: Bounding box as (min_lat, min_lon, max_lat, max_lon)
            tags: Dictionary of OSM tags to filter by
            element_types: List of element types ('node', 'way', 'relation').
                          Defaults to ['node', 'way', 'relation']
            max_items: Maximum number of items to return

        Returns:
            Tuple of (list of element dicts with metadata, api_info dict, question string)
        """
        if element_types is None:
            element_types = ['node', 'way', 'relation']

        # Build and execute query
        query = self._build_overpass_query(element_types, tags, bbox)

        response = self._execute_query(query)

        # Extract elements
        elements = response.get('elements', [])

        node_lookup = {
            elem['id']: (elem.get('lat'), elem.get('lon'))
            for elem in elements
            if elem.get('type') == 'node'
            and elem.get('lat') is not None
            and elem.get('lon') is not None
        }

        # Filter out node references
        main_elements = [
            elem for elem in elements
            if 'tags' in elem
        ]

        # Format with full metadata
        items = [self._format_element(elem, include_metadata=True, node_lookup=node_lookup)
                for elem in main_elements[:max_items]]

        # Build tag description
        tag_desc = ', '.join([f'{k}={v}' for k, v in tags.items()])

        question = (
            f"枚举边界框 {bbox} 内所有标签为 {tag_desc} 的地图要素（含元数据）"
        )

        api_info = {
            "api_endpoint": self.BASE_URL,
            "method": "POST",
            "parameters": {
                "query": query[:200] + "..." if len(query) > 200 else query,
                "bbox": bbox,
                "tags": tags,
                "element_types": element_types
            },
            "authentication": "None",
            "rate_limit": "Fair use policy (no hard limit, ~1 query/second recommended)",
            "documentation": "https://wiki.openstreetmap.org/wiki/Overpass_API",
            "metadata_fields": ["id", "type", "lat", "lon", "tags", "version", "changeset", "timestamp", "user"]
        }

        return items, api_info, question

    def fetch_within_radius(
        self,
        lat: float,
        lon: float,
        radius_m: int,
        tags: Dict[str, str],
        element_types: Optional[List[str]] = None,
        max_items: int = 10000
    ) -> Tuple[List[Dict], Dict, str]:
        """Fetch OSM elements within a radius of a point.

        This method is used for queries like "Find all hospitals within 5km of coordinates".

        Args:
            lat: Latitude of center point
            lon: Longitude of center point
            radius_m: Radius in meters
            tags: Dictionary of OSM tags to filter by
            element_types: List of element types. Defaults to ['node', 'way', 'relation']
            max_items: Maximum number of items to return

        Returns:
            Tuple of (list of element dicts with metadata, api_info dict, question string)
        """
        if element_types is None:
            element_types = ['node', 'way', 'relation']

        # Build and execute query
        query = self._build_radius_query(lat, lon, radius_m, element_types, tags)

        response = self._execute_query(query)

        # Extract elements
        elements = response.get('elements', [])

        node_lookup = {
            elem['id']: (elem.get('lat'), elem.get('lon'))
            for elem in elements
            if elem.get('type') == 'node'
            and elem.get('lat') is not None
            and elem.get('lon') is not None
        }

        # Filter out node references
        main_elements = [
            elem for elem in elements
            if 'tags' in elem
        ]

        # Format with full metadata
        items = [self._format_element(elem, include_metadata=True, node_lookup=node_lookup)
                for elem in main_elements[:max_items]]

        # Build tag description
        tag_desc = ', '.join([f'{k}={v}' for k, v in tags.items()])

        question = (
            f"枚举坐标 ({lat}, {lon}) 半径 {radius_m}米 内所有标签为 {tag_desc} 的地图要素"
        )

        api_info = {
            "api_endpoint": self.BASE_URL,
            "method": "POST",
            "parameters": {
                "query": query[:200] + "..." if len(query) > 200 else query,
                "center": {"lat": lat, "lon": lon},
                "radius_m": radius_m,
                "tags": tags,
                "element_types": element_types
            },
            "authentication": "None",
            "rate_limit": "Fair use policy (no hard limit, ~1 query/second recommended)",
            "documentation": "https://wiki.openstreetmap.org/wiki/Overpass_API",
            "metadata_fields": ["id", "type", "lat", "lon", "tags", "version", "changeset", "timestamp", "user"]
        }

        return items, api_info, question

    # Advanced filter methods

    def filter_by_tag(
        self,
        elements: List[Dict],
        tag_key: str,
        tag_value: str
    ) -> List[Dict]:
        """Filter elements by a specific tag.

        Args:
            elements: List of elements with metadata
            tag_key: Tag key to filter by
            tag_value: Tag value to match

        Returns:
            Filtered list of elements
        """
        return [
            elem for elem in elements
            if elem.get('tags', {}).get(tag_key) == tag_value
        ]

    def filter_with_playground(self, elements: List[Dict]) -> List[Dict]:
        """Filter parks that have a playground.

        This answers the advanced question:
        "List all public parks in a specific city that have a playground."

        Args:
            elements: List of park elements with metadata

        Returns:
            Parks that have playground=yes tag
        """
        results = []
        for elem in elements:
            tags = elem.get('tags', {})
            value = tags.get('playground')

            if value:
                normalized = value.lower()
                if normalized not in {'no', '0', 'false', 'off'}:
                    results.append(elem)
                    continue

            if tags.get('leisure') == 'playground':
                results.append(elem)

        return results

    def get_connected_lines(self, station_elements: List[Dict]) -> List[Dict]:
        """Get subway stations with their connected line information.

        This answers the advanced question:
        "Enumerate all subway stations in a city and list their connecting lines."

        Args:
            station_elements: List of subway station elements

        Returns:
            List of stations with extracted line/network information
        """
        results = []
        for elem in station_elements:
            tags = elem.get('tags', {})

            # Extract line information from various tag formats
            lines = []

            # Check for line tag
            if 'line' in tags:
                lines.append(tags['line'])

            # Check for network tag
            network = tags.get('network', 'Unknown')

            # Check for ref tag (line reference number)
            if 'ref' in tags:
                lines.append(tags['ref'])

            # Create result with line info
            result = elem.copy()
            result['connected_lines'] = lines if lines else ['No line info']
            result['network'] = network

            results.append(result)

        return results

    def filter_by_name_pattern(
        self,
        elements: List[Dict],
        pattern: str
    ) -> List[Dict]:
        """Filter elements by name matching a regex pattern.

        Args:
            elements: List of elements with metadata
            pattern: Regular expression pattern to match against name tag

        Returns:
            Elements with names matching the pattern
        """
        regex = re.compile(pattern, re.IGNORECASE)
        return [
            elem for elem in elements
            if 'name' in elem.get('tags', {})
            and regex.search(elem['tags']['name'])
        ]

    def filter_by_update_time(
        self,
        elements: List[Dict],
        days_ago: int
    ) -> List[Dict]:
        """Filter elements updated within the last N days.

        Args:
            elements: List of elements with metadata
            days_ago: Number of days to look back

        Returns:
            Elements updated within the specified time period
        """
        cutoff_date = datetime.now() - timedelta(days=days_ago)

        results = []
        for elem in elements:
            timestamp_str = elem.get('timestamp')
            if timestamp_str:
                try:
                    # Parse ISO format timestamp
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace('Z', '+00:00')
                    )
                    # Make naive for comparison
                    timestamp = timestamp.replace(tzinfo=None)

                    if timestamp >= cutoff_date:
                        results.append(elem)
                except (ValueError, AttributeError):
                    # Skip elements with invalid timestamps
                    continue

        return results

    def filter_wheelchair_accessible(self, elements: List[Dict]) -> List[Dict]:
        """Filter elements that are wheelchair accessible.

        Args:
            elements: List of elements with metadata

        Returns:
            Elements tagged as wheelchair accessible
        """
        return [
            elem for elem in elements
            if elem.get('tags', {}).get('wheelchair') == 'yes'
        ]

    def get_unique_tag_values(
        self,
        elements: List[Dict],
        tag_key: str
    ) -> List[str]:
        """Get all unique values for a specific tag.

        Useful for queries like "What are all the cuisine types available?"

        Args:
            elements: List of elements with metadata
            tag_key: Tag key to extract values from

        Returns:
            Sorted list of unique tag values
        """
        values = set()
        for elem in elements:
            value = elem.get('tags', {}).get(tag_key)
            if value:
                values.add(value)

        return sorted(list(values))

    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between two coordinates using Haversine formula.

        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate

        Returns:
            Distance in meters
        """
        # Earth radius in meters
        R = 6371000

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    def get_domain_name(self, **kwargs) -> str:
        """Return domain name for file naming.

        Args:
            **kwargs: Query parameters (bbox or coordinates)

        Returns:
            Domain name string for file naming
        """
        bbox = kwargs.get('bbox')
        if bbox:
            return f"osm_bbox_{bbox[0]}_{bbox[1]}"

        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        if lat and lon:
            return f"osm_point_{lat}_{lon}"

        return "openstreetmap"

    def get_metadata(self, **kwargs) -> Dict:
        """Return metadata about the query.

        Args:
            **kwargs: Query parameters

        Returns:
            Metadata dictionary
        """
        metadata = {
            "api": "OpenStreetMap Overpass API",
            "requires_auth": False
        }

        if 'bbox' in kwargs:
            metadata['bbox'] = kwargs['bbox']
            metadata['query_type'] = 'bounding_box'

        if 'lat' in kwargs and 'lon' in kwargs:
            metadata['center'] = {
                'lat': kwargs['lat'],
                'lon': kwargs['lon']
            }
            if 'radius_m' in kwargs:
                metadata['radius_m'] = kwargs['radius_m']
            metadata['query_type'] = 'radius'

        if 'tags' in kwargs:
            metadata['tags'] = kwargs['tags']

        return metadata
