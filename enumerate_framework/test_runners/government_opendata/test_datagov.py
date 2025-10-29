"""
Data.gov CKAN API - Structured Tests

This runner exercises the DataGovFetcher with:
- Basic enumeration by organization and keyword query
- Advanced questions from GEMINI.md:
  1) NASA + Mars (keyword within org)
  2) Air quality + CSV + updated in last 30 days
  3) Department of Commerce + GeoJSON format

Outputs JSON under output/api_tests/government_opendata/.
"""

import sys
from pathlib import Path

# Support both module import and direct execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from ..utils import save_result, create_test_result, print_header


def run(test_config=None):
    """Run Data.gov tests and save JSON outputs.

    Args:
        test_config: Optional dict with overrides.
    Returns:
        list of test result dicts.
    """
    print_header("测试 Data.gov CKAN API - 政府/开放数据")

    from fetchers.datagov import DataGovFetcher

    # Defaults chosen to be representative and deterministic
    config = {
        "organizations": [
            {"id": "nasa-gov", "name": "NASA"},
            {"id": "doc-gov", "name": "Department of Commerce"},
        ],
        "queries": [
            {"query": "air quality", "description": "空气质量"},
        ],
        "max_items_per_org": 5000,
        "max_items_per_query": 3000,
        "recent_days": 30,
    }

    if test_config:
        config.update(test_config)

    fetcher = DataGovFetcher()
    results = []

    # 1) Basic: enumerate datasets by organization (NASA)
    org = config["organizations"][0]
    datasets, api_info, question = fetcher.fetch_datasets_by_org(
        organization=org["id"], include_metadata=True, max_items=config["max_items_per_org"]
    )
    results.append(
        create_test_result(
            identifier=f"{org['id']}",
            question=question,
            api_info=api_info,
            data=datasets,
            data_key="datasets",
            organization=org["name"],
            organization_id=org["id"],
        )
    )

    # 2) Advanced Q1: NASA + Mars
    mars_in_nasa = fetcher.filter_by_keyword(datasets, "Mars")
    results.append(
        create_test_result(
            identifier=f"{org['id']}_mars",
            question="列出NASA组织中所有与'Mars'相关的数据集",
            api_info=api_info,
            data=mars_in_nasa,
            data_key="datasets",
            organization=org["name"],
            filter_keyword="Mars",
            total_org_datasets=len(datasets),
        )
    )

    # 3) Advanced Q2: Air quality + CSV + updated in last N days
    query = config["queries"][0]["query"]
    aq_datasets, aq_api_info, _ = fetcher.fetch_datasets_by_query(
        query=query, include_metadata=True, max_items=config["max_items_per_query"]
    )
    aq_csv = fetcher.filter_by_format(aq_datasets, "CSV")
    aq_csv_recent = fetcher.filter_by_update_time(aq_csv, days_ago=config["recent_days"])
    results.append(
        create_test_result(
            identifier="air_quality_csv_recent",
            question=f"列出关于'空气质量'的CSV格式数据集（最近{config['recent_days']}天更新）",
            api_info=aq_api_info,
            data=aq_csv_recent,
            data_key="datasets",
            query=query,
            format="CSV",
            days_ago=config["recent_days"],
            total_query_results=len(aq_datasets),
            total_csv=len(aq_csv),
        )
    )

    # 4) Advanced Q3: Department of Commerce + GeoJSON
    org_doc = config["organizations"][1]
    doc_datasets, doc_api_info, _ = fetcher.fetch_datasets_by_org(
        organization=org_doc["id"], include_metadata=True, max_items=config["max_items_per_org"]
    )
    doc_geojson = fetcher.filter_by_format(doc_datasets, "GeoJSON")
    results.append(
        create_test_result(
            identifier=f"{org_doc['id']}_geojson",
            question="列出Department of Commerce所有GeoJSON格式的数据集",
            api_info=doc_api_info,
            data=doc_geojson,
            data_key="datasets",
            organization=org_doc["name"],
            format="GeoJSON",
            total_org_datasets=len(doc_datasets),
        )
    )

    # Save under government_opendata
    save_result(
        "government_opendata/datagov",
        {
            "api_name": "Data.gov CKAN API",
            "category": "government_opendata",
            "requires_auth": False,
            "description": "政府开放数据的完整枚举与元数据丰富回答",
            "config": config,
            "tests": results,
        },
    )

    return results


if __name__ == "__main__":
    run()

