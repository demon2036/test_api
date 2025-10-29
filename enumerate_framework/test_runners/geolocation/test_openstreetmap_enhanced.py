"""
Enhanced OpenStreetMap Overpass API tests focusing on the
"Enumerate All" principles:
- Precision: explicit tag filters and deterministic sorting
- Completeness: full pagination for bounding-box/radius queries
- Verifiability: direct Overpass API usage with recorded parameters
- Determinism: stable ordering using distance, timestamps, or line counts

The tests cover the advanced questions described in the project brief:
1. Find all hospitals within a 5 km radius of a coordinate (ordered by distance)
2. List all public parks in a city that have a playground (ordered by recent edits)
3. Enumerate all subway stations in a city and list their connected lines
"""

import os
import sys
import time
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

# Ensure enumerate_framework package root is on sys.path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
)

from test_runners.utils import create_test_result, print_header, save_result
from fetchers.openstreetmap import OpenStreetMapFetcher


def _parse_iso(ts: Optional[str]) -> Optional[datetime]:
    """Parse Overpass timestamp into a datetime object."""
    if not ts:
        return None
    try:
        # Overpass timestamps use Z suffix; convert to +00:00 for fromisoformat
        parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if parsed.tzinfo:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError:
        return None


def _format_address(tags: Dict[str, str]) -> Dict[str, Optional[str]]:
    """Extract common address tags into a structured dict."""
    return {
        "street": tags.get("addr:street"),
        "city": tags.get("addr:city"),
        "postcode": tags.get("addr:postcode"),
        "housenumber": tags.get("addr:housenumber"),
    }


def _fetch_with_retry(
    fetch_callable: Callable[[], tuple],
    retries: int,
    delay: float,
    context: str,
):
    """Execute a callable with simple retry/backoff."""
    last_exc: Optional[Exception] = None
    for attempt in range(retries):
        try:
            return fetch_callable()
        except Exception as exc:
            last_exc = exc
            if attempt < retries - 1:
                wait = delay * (attempt + 1)
                print(
                    f"  ⚠️ {context} 请求失败（第 {attempt + 1}/{retries} 次），"
                    f"{wait:.1f}s 后重试: {exc}"
                )
                time.sleep(wait)
            else:
                raise last_exc


def run(test_config: Optional[Dict] = None) -> List[Dict]:
    """Execute enhanced OpenStreetMap tests and persist JSON output."""
    print_header("OpenStreetMap Overpass API (Enhanced)")

    fetcher = OpenStreetMapFetcher()

    # Default configuration concentrates on Tokyo to keep response sizes manageable.
    config = {
        "delay_seconds": 1.2,
        "retry_delay_seconds": 3.0,
        "max_retries": 3,
        "max_items": 750,
        "radius_queries": [
            {
                "name": "Tokyo - Shinjuku",
                "center": {"lat": 35.690921, "lon": 139.700257},
                "radius_m": 5000,
                "tags": {"amenity": "hospital"},
            }
        ],
        "bbox_queries": [
            {
                "name": "Tokyo - Central",
                "bbox": (35.63, 139.65, 35.74, 139.82),
                "tags": {"leisure": "park"},
                "focus": "playground",
            }
        ],
        "subway_queries": [
            {
                "name": "Tokyo - Central",
                "bbox": (35.63, 139.65, 35.74, 139.82),
                "tags": {"railway": "station", "station": "subway"},
            }
        ],
    }

    if test_config:
        for key, value in test_config.items():
            config[key] = value

    all_results: List[Dict] = []

    # ------------------------------------------------------------------
    # Advanced Question 1: Hospitals within radius ordered by distance
    # ------------------------------------------------------------------
    print("\n--- 半径查询：医院 ---")
    for query in config["radius_queries"]:
        try:
            hospitals, api_info, _ = _fetch_with_retry(
                lambda: fetcher.fetch_within_radius(
                    lat=query["center"]["lat"],
                    lon=query["center"]["lon"],
                    radius_m=query["radius_m"],
                    tags=query["tags"],
                    max_items=config["max_items"],
                ),
                config["max_retries"],
                config["retry_delay_seconds"],
                f"{query['name']} 医院半径查询",
            )
            enriched = []
            for hospital in hospitals:
                lat = hospital.get("lat")
                lon = hospital.get("lon")
                if lat is None or lon is None:
                    continue

                tags = hospital.get("tags", {})
                distance = fetcher.calculate_distance(
                    query["center"]["lat"],
                    query["center"]["lon"],
                    lat,
                    lon,
                )

                enriched.append(
                    {
                        "id": hospital["id"],
                        "name": tags.get("name", "未命名"),
                        "distance_m": round(distance, 1),
                        "lat": lat,
                        "lon": lon,
                        "emergency": tags.get("emergency"),
                        "wheelchair": tags.get("wheelchair"),
                        "beds": tags.get("healthcare:beds") or tags.get("beds"),
                        "opening_hours": tags.get("opening_hours"),
                        "operator": tags.get("operator"),
                        "phone": tags.get("phone"),
                        "last_edit": hospital.get("timestamp"),
                        "version": hospital.get("version"),
                        "changeset": hospital.get("changeset"),
                        "editor": hospital.get("user"),
                        "address": _format_address(tags),
                    }
                )

            enriched.sort(key=lambda item: item["distance_m"])
            for idx, item in enumerate(enriched, start=1):
                item["rank"] = idx

            question = (
                f"枚举 {query['name']} 半径 {query['radius_m']} 米内所有医院，"
                "按距离升序排序并包含急诊/无障碍等元数据"
            )

            result = create_test_result(
                identifier=f"{query['name'].replace(' ', '_')}_hospitals_radius",
                question=question,
                api_info=api_info,
                data=enriched,
                data_key="hospitals",
                area=query["name"],
                query_type="radius",
                center=query["center"],
                radius_m=query["radius_m"],
                tag_filters=query["tags"],
                total_raw=len(hospitals),
                metadata_fields=[
                    "rank",
                    "distance_m",
                    "emergency",
                    "wheelchair",
                    "beds",
                    "opening_hours",
                    "operator",
                    "phone",
                    "address",
                ],
                sort_field="distance_m",
            )

            all_results.append(result)
            print(f"  ✓ {query['name']}: {len(enriched)} 家医院按距离排序")
            time.sleep(config["delay_seconds"])

        except Exception as exc:
            print(f"  ✗ {query['name']} 查询失败: {exc}")

    # ------------------------------------------------------------------
    # Advanced Question 2: Parks with playground metadata
    # ------------------------------------------------------------------
    print("\n--- 公园查询：带游乐场 ---")
    for query in config["bbox_queries"]:
        try:
            parks, api_info, _ = _fetch_with_retry(
                lambda: fetcher.fetch_with_metadata(
                    bbox=query["bbox"],
                    tags=query["tags"],
                    max_items=config["max_items"],
                ),
                config["max_retries"],
                config["retry_delay_seconds"],
                f"{query['name']} 公园枚举",
            )

            playground_parks = fetcher.filter_with_playground(parks)

            enriched = []
            for park in playground_parks:
                tags = park.get("tags", {})
                enriched.append(
                    {
                        "id": park["id"],
                        "name": tags.get("name", "未命名"),
                        "lat": park.get("lat"),
                        "lon": park.get("lon"),
                        "has_playground_tag": tags.get("playground") == "yes",
                        "playground_notes": tags.get("playground"),
                        "surface": tags.get("surface"),
                        "operator": tags.get("operator"),
                        "opening_hours": tags.get("opening_hours"),
                        "access": tags.get("access"),
                        "toilets": tags.get("toilets"),
                        "drinking_water": tags.get("drinking_water"),
                        "last_edit": park.get("timestamp"),
                        "version": park.get("version"),
                        "editor": park.get("user"),
                        "address": _format_address(tags),
                    }
                )

            enriched.sort(
                key=lambda item: _parse_iso(item["last_edit"]) or datetime.min,
                reverse=True,
            )
            for idx, item in enumerate(enriched, start=1):
                item["rank_recent_edit"] = idx

            question = (
                f"列出 {query['name']} 范围内所有带游乐场的公园，"
                "按最近编辑时间排序并记录设施元数据"
            )

            result = create_test_result(
                identifier=f"{query['name'].replace(' ', '_')}_parks_playground",
                question=question,
                api_info=api_info,
                data=enriched,
                data_key="parks",
                area=query["name"],
                query_type="bbox",
                bbox=query["bbox"],
                tag_filters=query["tags"],
                total_raw=len(parks),
                total_filtered=len(playground_parks),
                metadata_fields=[
                    "rank_recent_edit",
                    "has_playground_tag",
                    "surface",
                    "operator",
                    "opening_hours",
                    "access",
                    "toilets",
                    "drinking_water",
                ],
                sort_field="rank_recent_edit",
            )

            all_results.append(result)
            print(f"  ✓ {query['name']}: {len(enriched)} 个公园带游乐场标签")
            time.sleep(config["delay_seconds"])

        except Exception as exc:
            print(f"  ✗ {query['name']} 查询失败: {exc}")

    # ------------------------------------------------------------------
    # Advanced Question 3: Subway stations with connected lines
    # ------------------------------------------------------------------
    print("\n--- 地铁站查询：线路枚举 ---")
    for query in config["subway_queries"]:
        try:
            stations, api_info, _ = _fetch_with_retry(
                lambda: fetcher.fetch_with_metadata(
                    bbox=query["bbox"],
                    tags=query["tags"],
                    element_types=["node"],
                    max_items=config["max_items"],
                ),
                config["max_retries"],
                config["retry_delay_seconds"],
                f"{query['name']} 地铁站枚举",
            )

            stations_with_lines = fetcher.get_connected_lines(stations)

            enriched = []
            for station in stations_with_lines:
                tags = station.get("tags", {})
                lines = station.get("connected_lines", [])
                enriched.append(
                    {
                        "id": station["id"],
                        "name": tags.get("name", "未命名"),
                        "lat": station.get("lat"),
                        "lon": station.get("lon"),
                        "network": station.get("network"),
                        "connected_lines": lines,
                        "line_count": len(lines),
                        "ref": tags.get("ref"),
                        "operator": tags.get("operator"),
                        "wheelchair": tags.get("wheelchair"),
                        "station_levels": tags.get("station"),
                        "last_edit": station.get("timestamp"),
                        "version": station.get("version"),
                        "editor": station.get("user"),
                        "address": _format_address(tags),
                    }
                )

            enriched.sort(key=lambda item: (-item["line_count"], item["name"]))
            for idx, item in enumerate(enriched, start=1):
                item["rank_by_lines"] = idx
                item["is_interchange"] = item["line_count"] > 1

            question = (
                f"枚举 {query['name']} 区域内所有地铁站，"
                "按连接线路数量排序并列出线路/无障碍等元数据"
            )

            result = create_test_result(
                identifier=f"{query['name'].replace(' ', '_')}_subway_lines",
                question=question,
                api_info=api_info,
                data=enriched,
                data_key="stations",
                area=query["name"],
                query_type="bbox",
                bbox=query["bbox"],
                tag_filters=query["tags"],
                metadata_fields=[
                    "rank_by_lines",
                    "connected_lines",
                    "network",
                    "operator",
                    "wheelchair",
                    "is_interchange",
                    "line_count",
                    "ref",
                ],
                sort_field="line_count",
            )

            all_results.append(result)
            print(f"  ✓ {query['name']}: {len(enriched)} 个地铁站完成线路枚举")
            time.sleep(config["delay_seconds"])

        except Exception as exc:
            print(f"  ✗ {query['name']} 查询失败: {exc}")

    # ------------------------------------------------------------------
    # Persist summary JSON (mirrors enhanced AI/ML structure)
    # ------------------------------------------------------------------
    summary = {
        "api_name": "OpenStreetMap Overpass API - Enhanced Tests",
        "requires_auth": False,
        "description": (
            "围绕东京核心城区的 Overpass API 枚举测试，涵盖医院半径查询、"
            "带游乐场公园筛选以及地铁站连接线路枚举，突出可验证的排序和丰富元数据。"
        ),
        "metadata_guidelines": [
            "医院：distance_m、emergency、wheelchair、beds、opening_hours",
            "公园：has_playground_tag、opening_hours、surface、operator",
            "地铁站：connected_lines、line_count、network、wheelchair",
        ],
        "tests": all_results,
        "config": config,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    save_result("geolocation/openstreetmap_enhanced", summary)
    print("所有增强测试完成 ✅")

    return all_results


if __name__ == "__main__":
    run()
