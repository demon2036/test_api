"""
Data.gov API Test Runner

This module tests the DataGovFetcher with various organizations and queries.

Covers:
- Basic enumeration (datasets by organization, datasets by search query)
- All 3 advanced questions from GEMINI.md:
  1. List all datasets from the 'NASA' organization related to 'Mars'
  2. Find all CSV datasets related to 'air quality' updated in the last month
  3. Enumerate all datasets from the 'Department of Commerce' that are available in GeoJSON format
- Additional metadata filtering tests
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from test_runners.utils import save_result, create_test_result, print_header


def run(test_config=None):
    """Run Data.gov API tests

    Args:
        test_config: Optional configuration dictionary to override defaults
    """
    print_header("测试 Data.gov CKAN API")

    from fetchers.datagov import DataGovFetcher

    # Default configuration with test organizations and queries
    config = {
        "test_organizations": [
            {"id": "nasa-gov", "name": "NASA"},
            {"id": "doc-gov", "name": "Department of Commerce"},
            {"id": "noaa-gov", "name": "NOAA"},
            {"id": "epa-gov", "name": "EPA"}
        ],
        "test_queries": [
            {"query": "air quality", "description": "空气质量"},
            {"query": "climate change", "description": "气候变化"},
            {"query": "Mars", "description": "火星"}
        ],
        "max_items_per_org": 10000,
        "max_items_per_query": 5000
    }

    # Merge user config if provided
    if test_config:
        config.update(test_config)

    fetcher = DataGovFetcher()
    all_results = []

    # ========================================
    # Part 1: Basic Enumeration Tests by Organization
    # ========================================
    print("\n" + "-"*80)
    print("Part 1: 基本枚举测试（按组织）")
    print("-"*80)

    for org in config["test_organizations"][:2]:  # Test NASA and Department of Commerce
        print(f"\n测试组织: {org['name']} ({org['id']})")

        try:
            datasets, api_info, question = fetcher.fetch_datasets_by_org(
                organization=org['id'],
                include_metadata=True,
                max_items=config["max_items_per_org"]
            )

            result = create_test_result(
                identifier=f"{org['id']}",
                question=question,
                api_info=api_info,
                data=datasets,
                data_key="datasets",
                organization=org['name'],
                organization_id=org['id']
            )

            all_results.append(result)

            print(f"  ✓ 找到 {len(datasets)} 个数据集")

            # Show sample datasets
            if datasets:
                for i, ds in enumerate(datasets[:3], 1):
                    title = ds.get('title', 'Untitled')
                    formats = ', '.join(ds.get('formats', []))
                    print(f"    {i}. {title}")
                    print(f"       格式: {formats}")

            # Show statistics
            stats = fetcher.get_dataset_stats(datasets)
            print(f"  统计:")
            print(f"    总资源数: {stats['total_resources']}")
            print(f"    平均资源/数据集: {stats['avg_resources_per_dataset']:.1f}")
            print(f"    唯一格式: {len(stats['unique_formats'])}")

            time.sleep(2)  # Rate limiting

        except Exception as e:
            print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 2: Advanced Question 1
    # "List all datasets from the 'NASA' organization related to 'Mars'"
    # ========================================
    print("\n" + "-"*80)
    print("Part 2: 高级问题 1 - NASA组织中与'Mars'相关的数据集")
    print("-"*80)

    try:
        org = config["test_organizations"][0]  # NASA
        print(f"测试组织: {org['name']}")

        # First fetch all NASA datasets
        nasa_datasets, api_info, question = fetcher.fetch_datasets_by_org(
            organization=org['id'],
            include_metadata=True,
            max_items=config["max_items_per_org"]
        )

        print(f"  总共找到 {len(nasa_datasets)} 个NASA数据集")

        # Filter datasets related to Mars
        mars_datasets = fetcher.filter_by_keyword(nasa_datasets, "Mars")

        result = create_test_result(
            identifier=f"{org['id']}_mars",
            question=f"枚举 NASA 所有与 'Mars' 相关的数据集",
            api_info=api_info,
            data=mars_datasets,
            data_key="datasets",
            organization=org['name'],
            filter_keyword="Mars",
            total_org_datasets=len(nasa_datasets)
        )

        all_results.append(result)

        print(f"  ✓ 找到 {len(mars_datasets)} 个与'Mars'相关的数据集")

        # Show sample Mars datasets
        for i, ds in enumerate(mars_datasets[:5], 1):
            title = ds.get('title', 'Untitled')
            formats = ', '.join(ds.get('formats', []))
            print(f"    {i}. {title}")
            print(f"       格式: {formats}")

        time.sleep(2)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 3: Advanced Question 2
    # "Find all CSV datasets related to 'air quality' updated in the last month"
    # ========================================
    print("\n" + "-"*80)
    print("Part 3: 高级问题 2 - 最近30天更新的CSV格式'空气质量'数据集")
    print("-"*80)

    try:
        query = "air quality"
        print(f"搜索查询: {query}")

        # Search for air quality datasets
        air_quality_datasets, api_info, question = fetcher.fetch_datasets_by_query(
            query=query,
            include_metadata=True,
            max_items=config["max_items_per_query"]
        )

        print(f"  总共找到 {len(air_quality_datasets)} 个相关数据集")

        # Filter for CSV format
        csv_datasets = fetcher.filter_by_format(air_quality_datasets, "CSV")
        print(f"  其中CSV格式: {len(csv_datasets)} 个")

        # Filter by update time (last 30 days)
        recent_csv_datasets = fetcher.filter_by_update_time(csv_datasets, days_ago=30)

        result = create_test_result(
            identifier="air_quality_csv_recent",
            question=f"枚举所有关于'空气质量'的CSV格式数据集（最近30天更新）",
            api_info=api_info,
            data=recent_csv_datasets,
            data_key="datasets",
            query=query,
            format="CSV",
            days_ago=30,
            total_query_results=len(air_quality_datasets),
            total_csv=len(csv_datasets)
        )

        all_results.append(result)

        print(f"  ✓ 找到 {len(recent_csv_datasets)} 个最近更新的CSV数据集")

        # Show sample datasets
        for i, ds in enumerate(recent_csv_datasets[:3], 1):
            title = ds.get('title', 'Untitled')
            modified = ds.get('metadata_modified', '')[:10]  # Just the date
            org = ds.get('organization_title', 'Unknown')
            print(f"    {i}. {title}")
            print(f"       组织: {org}, 更新: {modified}")

        time.sleep(2)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 4: Advanced Question 3
    # "Enumerate all datasets from the 'Department of Commerce' that are available in GeoJSON format"
    # ========================================
    print("\n" + "-"*80)
    print("Part 4: 高级问题 3 - Department of Commerce的GeoJSON格式数据集")
    print("-"*80)

    try:
        org = config["test_organizations"][1]  # Department of Commerce
        print(f"测试组织: {org['name']}")

        # First fetch all DOC datasets
        doc_datasets, api_info, question = fetcher.fetch_datasets_by_org(
            organization=org['id'],
            include_metadata=True,
            max_items=config["max_items_per_org"]
        )

        print(f"  总共找到 {len(doc_datasets)} 个数据集")

        # Filter for GeoJSON format
        geojson_datasets = fetcher.filter_by_format(doc_datasets, "GeoJSON")

        result = create_test_result(
            identifier=f"{org['id']}_geojson",
            question=f"枚举 Department of Commerce 所有 GeoJSON 格式的数据集",
            api_info=api_info,
            data=geojson_datasets,
            data_key="datasets",
            organization=org['name'],
            format="GeoJSON",
            total_org_datasets=len(doc_datasets)
        )

        all_results.append(result)

        print(f"  ✓ 找到 {len(geojson_datasets)} 个GeoJSON格式数据集")

        # Show sample datasets
        for i, ds in enumerate(geojson_datasets[:5], 1):
            title = ds.get('title', 'Untitled')
            formats = ', '.join(ds.get('formats', []))
            print(f"    {i}. {title}")
            print(f"       所有格式: {formats}")

        time.sleep(2)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 5: Additional Metadata Filtering
    # ========================================
    print("\n" + "-"*80)
    print("Part 5: 其他元数据过滤测试")
    print("-"*80)

    # Test 5.1: Datasets by license
    print("\n5.1 开放许可证数据集（Creative Commons）")
    try:
        org = config["test_organizations"][0]  # NASA
        datasets, api_info, question = fetcher.fetch_datasets_by_org(
            organization=org['id'],
            include_metadata=True,
            max_items=1000
        )

        cc_datasets = fetcher.filter_by_license(datasets, "Creative Commons")

        result = create_test_result(
            identifier=f"{org['id']}_creative_commons",
            question=f"枚举 NASA 所有使用 Creative Commons 许可证的数据集",
            api_info=api_info,
            data=cc_datasets,
            data_key="datasets",
            organization=org['name'],
            license_pattern="Creative Commons",
            total_org_datasets=len(datasets)
        )

        all_results.append(result)

        print(f"  ✓ 找到 {len(cc_datasets)} 个Creative Commons数据集（共 {len(datasets)} 个）")

        time.sleep(2)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # Test 5.2: Datasets with multiple resources
    print("\n5.2 资源丰富的数据集（10+资源）")
    try:
        org = config["test_organizations"][2]  # NOAA
        datasets, api_info, question = fetcher.fetch_datasets_by_org(
            organization=org['id'],
            include_metadata=True,
            max_items=1000
        )

        rich_datasets = fetcher.filter_by_resource_count(datasets, min_count=10)

        result = create_test_result(
            identifier=f"{org['id']}_rich_resources",
            question=f"枚举 NOAA 所有有10个以上资源的数据集",
            api_info=api_info,
            data=rich_datasets,
            data_key="datasets",
            organization=org['name'],
            min_resources=10,
            total_org_datasets=len(datasets)
        )

        all_results.append(result)

        print(f"  ✓ 找到 {len(rich_datasets)} 个资源丰富的数据集（共 {len(datasets)} 个）")

        # Show examples with resource counts
        for i, ds in enumerate(rich_datasets[:3], 1):
            title = ds.get('title', 'Untitled')
            count = ds.get('resources_count', 0)
            print(f"    {i}. {title} ({count} 个资源)")

        time.sleep(2)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # Test 5.3: Format statistics
    print("\n5.3 数据格式统计")
    try:
        org = config["test_organizations"][0]  # NASA
        datasets, api_info, question = fetcher.fetch_datasets_by_org(
            organization=org['id'],
            include_metadata=True,
            max_items=1000
        )

        formats = fetcher.get_unique_formats(datasets)

        print(f"  ✓ NASA数据集使用的格式种类: {len(formats)}")
        print(f"  示例格式: {', '.join(formats[:15])}")

        # Count datasets per format
        format_counts = {}
        for fmt in formats[:10]:  # Top 10 formats
            count = len(fetcher.filter_by_format(datasets, fmt))
            format_counts[fmt] = count

        # Sort by count
        sorted_formats = sorted(format_counts.items(), key=lambda x: x[1], reverse=True)

        print(f"\n  前10种格式的使用频率:")
        for fmt, count in sorted_formats:
            print(f"    {fmt}: {count} 个数据集")

        result = {
            "question": f"统计 NASA 数据集的格式使用情况",
            "organization": org['name'],
            "total_formats": len(formats),
            "all_formats": formats,
            "format_counts": format_counts,
            "timestamp": all_results[0]['timestamp'] if all_results else None
        }

        all_results.append(result)

        time.sleep(2)

    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

    # ========================================
    # Part 6: Multi-Organization Comparison
    # ========================================
    print("\n" + "-"*80)
    print("Part 6: 跨组织对比")
    print("-"*80)

    comparison_data = []
    for org in config["test_organizations"]:
        try:
            # Get basic count for each organization
            datasets, _, _ = fetcher.fetch_datasets_by_org(
                organization=org['id'],
                include_metadata=True,
                max_items=config["max_items_per_org"]
            )

            stats = fetcher.get_dataset_stats(datasets)

            org_data = {
                "organization": org['name'],
                "organization_id": org['id'],
                "total_datasets": stats['total_datasets'],
                "total_resources": stats['total_resources'],
                "avg_resources": round(stats['avg_resources_per_dataset'], 2),
                "unique_formats": len(stats['unique_formats'])
            }

            comparison_data.append(org_data)

            print(f"\n{org['name']}:")
            print(f"  数据集数量: {org_data['total_datasets']}")
            print(f"  资源总数: {org_data['total_resources']}")
            print(f"  平均资源/数据集: {org_data['avg_resources']}")
            print(f"  格式种类: {org_data['unique_formats']}")

            time.sleep(2)

        except Exception as e:
            print(f"\n{org['name']}: 错误 - {str(e)}")

    # Save comparison result
    if comparison_data:
        result = {
            "question": "比较不同组织的数据集规模和多样性",
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
        "api_name": "Data.gov CKAN API",
        "requires_auth": False,
        "config": config,
        "total_tests": len(all_results),
        "tests": all_results
    }

    save_result("datagov", summary)

    print(f"\n总测试数: {len(all_results)}")
    print("所有测试已完成！")

    return all_results


if __name__ == "__main__":
    run()
