"""
OpenStreetMap Overpass API Test Runner

This module tests the OpenStreetMapFetcher with various queries across multiple cities.

Covers:
- Basic enumeration (hospitals, parks, subway stations, restaurants)
- All 3 advanced questions from GEMINI.md:
  1. Find all hospitals within a 5km radius of coordinates
  2. List all public parks that have a playground
  3. Enumerate all subway stations and list their connecting lines
- Additional metadata filtering tests
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from test_runners.utils import save_result, create_test_result, print_header


def run(test_config=None):
    """Run OpenStreetMap API tests

    Args:
        test_config: Optional configuration dictionary to override defaults
    """
    print_header("测试 OpenStreetMap Overpass API")

    from fetchers.openstreetmap import OpenStreetMapFetcher

    # Default configuration with test areas and queries
    config = {
        "test_areas": [
            {
                "name": "NYC Manhattan",
                "bbox": (40.7000, -74.0200, 40.8000, -73.9000),
                "center": {"lat": 40.7589, "lon": -73.9851},
                "radius_m": 5000
            },
            {
                "name": "San Francisco",
                "bbox": (37.7000, -122.5000, 37.8000, -122.4000),
                "center": {"lat": 37.7749, "lon": -122.4194},
                "radius_m": 5000
            },
            {
                "name": "London",
                "bbox": (51.4500, -0.2000, 51.5500, 0.0000),
                "center": {"lat": 51.5074, "lon": -0.1278},
                "radius_m": 5000
            },
            {
                "name": "Tokyo",
                "bbox": (35.6000, 139.6500, 35.7500, 139.8000),
                "center": {"lat": 35.6762, "lon": 139.6503},
                "radius_m": 5000
            }
        ],
        "basic_queries": [
            {"tags": {"amenity": "hospital"}, "description": "医院"},
            {"tags": {"leisure": "park"}, "description": "公园"},
            {"tags": {"railway": "station", "station": "subway"}, "description": "地铁站"},
            {"tags": {"amenity": "restaurant"}, "description": "餐厅"}
        ],
        "max_items": 10000
    }

    # Merge user config if provided
    if test_config:
        config.update(test_config)

    fetcher = OpenStreetMapFetcher()
    all_results = []

    # ========================================
    # Part 1: Basic Enumeration Tests
    # ========================================
    print("\n" + "-"*80)
    print("Part 1: 基本枚举测试（按边界框）")
    print("-"*80)

    for area in config["test_areas"]:
        print(f"\n测试区域: {area['name']}")
        print(f"  边界框: {area['bbox']}")

        for query in config["basic_queries"][:2]:  # Test hospitals and parks
            print(f"\n  查询: {query['description']}")

            try:
                items, api_info, question = fetcher.fetch_with_metadata(
                    bbox=area["bbox"],
                    tags=query["tags"],
                    max_items=config["max_items"]
                )

                result = create_test_result(
                    identifier=f"{area['name']}_{query['description']}",
                    question=question,
                    api_info=api_info,
                    data=items,
                    data_key="elements",
                    area=area['name'],
                    query_type="bbox",
                    tags=query["tags"]
                )

                all_results.append(result)

                print(f"    ✓ 找到 {len(items)} 个{query['description']}")

                # Show sample element
                if items:
                    sample = items[0]
                    name = sample.get('tags', {}).get('name', 'Unnamed')
                    print(f"    示例: {name} ({sample['type']}/{sample.get('tags', {}).get('amenity', sample.get('tags', {}).get('leisure', 'N/A'))})")

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                print(f"    ✗ 错误: {str(e)}")

    # ========================================
    # Part 2: Advanced Question 1
    # "Find all hospitals within 5km radius"
    # ========================================
    print("\n" + "-"*80)
    print("Part 2: 高级问题 1 - 半径范围内的医院（5公里）")
    print("-"*80)

    for area in config["test_areas"][:2]:  # Test Manhattan and San Francisco
        print(f"\n测试区域: {area['name']}")
        print(f"  中心点: ({area['center']['lat']}, {area['center']['lon']})")
        print(f"  半径: {area['radius_m']} 米")

        try:
            items, api_info, question = fetcher.fetch_within_radius(
                lat=area['center']['lat'],
                lon=area['center']['lon'],
                radius_m=area['radius_m'],
                tags={"amenity": "hospital"},
                max_items=config["max_items"]
            )

            result = create_test_result(
                identifier=f"{area['name']}_hospitals_radius",
                question=question,
                api_info=api_info,
                data=items,
                data_key="hospitals",
                area=area['name'],
                query_type="radius",
                radius_m=area['radius_m']
            )

            all_results.append(result)

            print(f"  ✓ 找到 {len(items)} 个医院")

            # Show top 3 hospitals with names
            for i, hospital in enumerate(items[:3], 1):
                name = hospital.get('tags', {}).get('name', 'Unnamed')
                emergency = hospital.get('tags', {}).get('emergency', 'N/A')
                print(f"    {i}. {name} (急诊: {emergency})")

            time.sleep(1)

        except Exception as e:
            print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 3: Advanced Question 2
    # "List all parks that have a playground"
    # ========================================
    print("\n" + "-"*80)
    print("Part 3: 高级问题 2 - 带游乐场的公园")
    print("-"*80)

    for area in config["test_areas"][:2]:  # Test Manhattan and San Francisco
        print(f"\n测试区域: {area['name']}")

        try:
            # First fetch all parks
            parks, api_info, question = fetcher.fetch_with_metadata(
                bbox=area["bbox"],
                tags={"leisure": "park"},
                max_items=config["max_items"]
            )

            print(f"  总共找到 {len(parks)} 个公园")

            # Filter parks with playgrounds
            parks_with_playground = fetcher.filter_with_playground(parks)

            result = create_test_result(
                identifier=f"{area['name']}_parks_with_playground",
                question=f"枚举 {area['name']} 所有带游乐场的公园",
                api_info=api_info,
                data=parks_with_playground,
                data_key="parks",
                area=area['name'],
                query_type="filtered",
                filter_type="playground",
                total_parks=len(parks)
            )

            all_results.append(result)

            print(f"  ✓ 找到 {len(parks_with_playground)} 个带游乐场的公园")

            # Show sample parks
            for i, park in enumerate(parks_with_playground[:3], 1):
                name = park.get('tags', {}).get('name', 'Unnamed')
                print(f"    {i}. {name}")

            time.sleep(1)

        except Exception as e:
            print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 4: Advanced Question 3
    # "Enumerate subway stations with connecting lines"
    # ========================================
    print("\n" + "-"*80)
    print("Part 4: 高级问题 3 - 地铁站及其连接线路")
    print("-"*80)

    for area in config["test_areas"][:3]:  # Test Manhattan, SF, London
        print(f"\n测试区域: {area['name']}")

        try:
            # Fetch subway stations
            stations, api_info, question = fetcher.fetch_with_metadata(
                bbox=area["bbox"],
                tags={"railway": "station", "station": "subway"},
                element_types=['node'],  # Stations are typically nodes
                max_items=config["max_items"]
            )

            print(f"  总共找到 {len(stations)} 个地铁站")

            # Extract line information
            stations_with_lines = fetcher.get_connected_lines(stations)

            result = create_test_result(
                identifier=f"{area['name']}_subway_stations",
                question=f"枚举 {area['name']} 所有地铁站及其连接线路",
                api_info=api_info,
                data=stations_with_lines,
                data_key="stations",
                area=area['name'],
                query_type="subway_with_lines"
            )

            all_results.append(result)

            print(f"  ✓ 找到 {len(stations_with_lines)} 个地铁站")

            # Show stations with line info
            for i, station in enumerate(stations_with_lines[:5], 1):
                name = station.get('tags', {}).get('name', 'Unnamed')
                lines = station.get('connected_lines', [])
                network = station.get('network', 'Unknown')
                print(f"    {i}. {name}")
                print(f"       网络: {network}, 线路: {', '.join(lines)}")

            time.sleep(1)

        except Exception as e:
            print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 5: Additional Metadata Filtering
    # ========================================
    print("\n" + "-"*80)
    print("Part 5: 其他元数据过滤测试")
    print("-"*80)

    # Test 5.1: Wheelchair accessible hospitals
    print("\n5.1 无障碍医院")
    try:
        area = config["test_areas"][0]  # Manhattan
        hospitals, api_info, question = fetcher.fetch_with_metadata(
            bbox=area["bbox"],
            tags={"amenity": "hospital"},
            max_items=config["max_items"]
        )

        wheelchair_hospitals = fetcher.filter_wheelchair_accessible(hospitals)

        result = create_test_result(
            identifier=f"{area['name']}_wheelchair_hospitals",
            question=f"枚举 {area['name']} 所有无障碍医院",
            api_info=api_info,
            data=wheelchair_hospitals,
            data_key="hospitals",
            area=area['name'],
            filter_type="wheelchair_accessible",
            total_hospitals=len(hospitals)
        )

        all_results.append(result)

        print(f"  ✓ 找到 {len(wheelchair_hospitals)} 个无障碍医院（共 {len(hospitals)} 个）")

        time.sleep(1)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # Test 5.2: Restaurants by cuisine type
    print("\n5.2 餐厅菜系统计")
    try:
        area = config["test_areas"][0]  # Manhattan
        restaurants, api_info, question = fetcher.fetch_with_metadata(
            bbox=area["bbox"],
            tags={"amenity": "restaurant"},
            max_items=500  # Limit to avoid long queries
        )

        cuisines = fetcher.get_unique_tag_values(restaurants, 'cuisine')

        print(f"  ✓ 找到 {len(restaurants)} 个餐厅")
        print(f"  ✓ 菜系种类: {len(cuisines)}")
        print(f"  示例菜系: {', '.join(cuisines[:10])}")

        # Create result with cuisine breakdown
        result = create_test_result(
            identifier=f"{area['name']}_restaurant_cuisines",
            question=f"统计 {area['name']} 餐厅的菜系种类",
            api_info=api_info,
            data=cuisines,
            data_key="cuisines",
            area=area['name'],
            total_restaurants=len(restaurants)
        )

        all_results.append(result)

        time.sleep(1)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # Test 5.3: Recently updated features
    print("\n5.3 最近更新的地图要素（30天内）")
    try:
        area = config["test_areas"][0]  # Manhattan
        parks, api_info, question = fetcher.fetch_with_metadata(
            bbox=area["bbox"],
            tags={"leisure": "park"},
            max_items=config["max_items"]
        )

        recent_parks = fetcher.filter_by_update_time(parks, days_ago=30)

        result = create_test_result(
            identifier=f"{area['name']}_recent_parks",
            question=f"枚举 {area['name']} 最近30天更新的公园",
            api_info=api_info,
            data=recent_parks,
            data_key="parks",
            area=area['name'],
            filter_type="recent_update",
            days_ago=30,
            total_parks=len(parks)
        )

        all_results.append(result)

        print(f"  ✓ 找到 {len(recent_parks)} 个最近更新的公园（共 {len(parks)} 个）")

        time.sleep(1)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 6: Multi-city Comparison
    # ========================================
    print("\n" + "-"*80)
    print("Part 6: 跨城市对比")
    print("-"*80)

    comparison_data = []
    for area in config["test_areas"]:
        try:
            # Count hospitals in each city
            hospitals, _, _ = fetcher.fetch_with_metadata(
                bbox=area["bbox"],
                tags={"amenity": "hospital"},
                max_items=config["max_items"]
            )

            # Count subway stations
            stations, _, _ = fetcher.fetch_with_metadata(
                bbox=area["bbox"],
                tags={"railway": "station", "station": "subway"},
                element_types=['node'],
                max_items=config["max_items"]
            )

            city_data = {
                "city": area['name'],
                "hospitals": len(hospitals),
                "subway_stations": len(stations)
            }

            comparison_data.append(city_data)

            print(f"\n{area['name']}:")
            print(f"  医院数量: {len(hospitals)}")
            print(f"  地铁站数量: {len(stations)}")

            time.sleep(1)

        except Exception as e:
            print(f"\n{area['name']}: 错误 - {str(e)}")

    # Save comparison result
    if comparison_data:
        result = {
            "question": "比较不同城市的医院和地铁站数量",
            "comparison_data": comparison_data,
            "timestamp": all_results[0]['timestamp'] if all_results else None
        }
        all_results.append(result)

    # ========================================
    # Save All Results
    # ========================================
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)

    summary = {
        "api_name": "OpenStreetMap Overpass API",
        "requires_auth": False,
        "config": config,
        "total_tests": len(all_results),
        "tests": all_results
    }

    save_result("openstreetmap", summary)

    print(f"\n总测试数: {len(all_results)}")
    print("所有测试已完成！")

    return all_results


if __name__ == "__main__":
    run()
