"""Zenodo API 测试运行器 - 基础枚举 + 元数据增强查询"""

import sys
import time
from collections import Counter
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from ...utils import save_result, create_test_result, print_header


def _format_record(record, index_map):
    """规范化Zenodo记录输出，附带核心元数据和体积信息"""
    idx = index_map.get(id(record), -1)
    size_bytes = record.get("total_size_bytes", 0) or 0
    size_gb = size_bytes / (1024 ** 3) if size_bytes else 0.0
    return {
        "rank": idx + 1 if idx >= 0 else None,
        "doi": record.get("doi"),
        "title": record.get("title"),
        "publication_date": record.get("publication_date"),
        "resource_type": record.get("resource_type"),
        "resource_subtype": record.get("resource_subtype"),
        "license": record.get("license"),
        "total_size_bytes": size_bytes,
        "size_gb": round(size_gb, 3),
        "version": record.get("version"),
        "creators": record.get("creators", []),
        "keywords": record.get("keywords", []),
    }


def run(test_config=None):
    """运行Zenodo API测试，整合基础枚举与元数据过滤场景"""
    print_header("测试 Zenodo API (基础 + 元数据增强)")

    from fetchers.academic_research.zenodo import ZenodoFetcher

    fetcher = ZenodoFetcher()

    # 默认配置 - 使用ORCID进行精确查询
    config = {
        "researchers": [
            {"orcid": "0000-0002-1825-0097", "name": "Joanna Rees"},
        ],
        "max_records": 200,
        "sleep_seconds": 1.0,
    }

    if test_config:
        config.update(test_config)

    all_results = []

    print("\n说明:")
    print("  Zenodo支持通过ORCID精确枚举研究者的所有记录，并提供文件体积、许可证等详细元数据。")
    print("  合并后的测试会输出排名及丰富结构化数据，便于验证过滤逻辑。\n")

    for researcher in config["researchers"]:
        orcid = researcher["orcid"]
        name = researcher.get("name", orcid)

        print(f"\n{'=' * 70}")
        print(f"测试研究者: {name} (ORCID: {orcid})")
        print(f"{'=' * 70}")

        records, api_info, base_question = fetcher.fetch_by_orcid_with_metadata(
            orcid=orcid,
            max_records=config["max_records"],
        )

        total_count = len(records)
        print(f"[基础问题] 列出所有记录 → 共 {total_count} 条")

        index_map = {id(record): idx for idx, record in enumerate(records)}
        formatted_records = [_format_record(record, index_map) for record in records]

        for record in formatted_records[:3]:
            print(
                f"  - #{record['rank']}: [{record.get('publication_date', 'N/A')}] "
                f"{(record.get('title') or '')[:70]}..."
            )

        base_result = create_test_result(
            identifier=orcid,
            question=base_question,
            api_info=api_info,
            data=formatted_records,
            data_key="records",
            orcid=orcid,
            researcher=name,
        )
        base_result["metadata_available"] = True
        base_result["notes"] = "包含DOI、资源类型、文件大小、许可证和创作者列表等核心元数据。"

        # 统计概况
        type_counts = Counter()
        license_counts = Counter()
        for record in records:
            type_counts[record.get("resource_type", "unknown")] += 1
            license_counts[record.get("license", "unknown")] += 1

        # ==================== 增强问题 1：大文件 (>1GB) ====================
        print(f"\n[增强问题 1/3] 列出所有大于1GB的数据集")
        large_records = fetcher.filter_by_size(records, min_size_gb=1.0)
        large_formatted = [_format_record(record, index_map) for record in large_records]
        large_percentage = len(large_records) / total_count * 100 if total_count else 0
        total_size_gb = sum(r.get("total_size_bytes", 0) for r in large_records) / (1024 ** 3)

        print(f"  ✓ 找到 {len(large_records)} 条（占比: {large_percentage:.1f}%）")
        for record in large_formatted[:3]:
            print(
                f"    - #{record['rank']}: [{record.get('resource_type')}] "
                f"{(record.get('title') or '')[:60]}..."
            )
            print(f"      大小: {record['size_gb']:.2f} GB")

        enhanced_result_1 = {
            "question": f"列出Zenodo中{name} (ORCID: {orcid})的大于1GB的所有记录",
            "filter_type": "size",
            "filter_value": ">=1GB",
            "total_count": len(large_records),
            "percentage": f"{large_percentage:.1f}%",
            "total_size_gb": f"{total_size_gb:.2f}",
            "records": large_formatted,
        }

        # ==================== 增强问题 2：Software类型 ====================
        print(f"\n[增强问题 2/3] 列出所有Software类型的记录")
        software_records = fetcher.filter_by_resource_type(records, "software")
        software_formatted = [_format_record(record, index_map) for record in software_records]
        software_percentage = len(software_records) / total_count * 100 if total_count else 0

        print(f"  ✓ 找到 {len(software_records)} 条（占比: {software_percentage:.1f}%）")
        for record in software_formatted[:3]:
            print(
                f"    - #{record['rank']}: [{record.get('publication_date', 'N/A')}] "
                f"{(record.get('title') or '')[:70]}..."
            )
            print(f"      许可证: {record.get('license')}")

        enhanced_result_2 = {
            "question": f"列出Zenodo中{name} (ORCID: {orcid})的所有Software类型记录",
            "filter_type": "resource_type",
            "filter_value": "software",
            "total_count": len(software_records),
            "percentage": f"{software_percentage:.1f}%",
            "resource_type_distribution": dict(type_counts),
            "records": software_formatted,
        }

        # ==================== 增强问题 3：Creative Commons许可 ====================
        print(f"\n[增强问题 3/3] 列出所有使用Creative Commons许可的记录")
        cc_records = fetcher.filter_by_license(records, "cc")
        cc_formatted = [_format_record(record, index_map) for record in cc_records]
        cc_percentage = len(cc_records) / total_count * 100 if total_count else 0

        print(f"  ✓ 找到 {len(cc_records)} 条（占比: {cc_percentage:.1f}%）")
        for record in cc_formatted[:3]:
            print(
                f"    - #{record['rank']}: [{record.get('publication_date', 'N/A')}] "
                f"{(record.get('title') or '')[:70]}..."
            )
            print(f"      许可证: {record.get('license')}")

        enhanced_result_3 = {
            "question": f"列出Zenodo中{name} (ORCID: {orcid})的所有使用Creative Commons许可的记录",
            "filter_type": "license",
            "filter_value": "cc",
            "total_count": len(cc_records),
            "percentage": f"{cc_percentage:.1f}%",
            "license_distribution": dict(license_counts),
            "records": cc_formatted,
        }

        researcher_result = {
            "researcher": name,
            "orcid": orcid,
            "base_test": base_result,
            "enhanced_tests": [
                enhanced_result_1,
                enhanced_result_2,
                enhanced_result_3,
            ],
            "api_info": api_info,
            "summary": {
                "total_records": total_count,
                "large_datasets": len(large_records),
                "software_records": len(software_records),
                "cc_licensed": len(cc_records),
                "resource_types": dict(type_counts),
                "licenses": dict(license_counts),
            },
        }

        all_results.append(researcher_result)

        if config.get("sleep_seconds"):
            time.sleep(config["sleep_seconds"])

    save_result(
        "academic_research/zenodo",
        {
            "api_name": "Zenodo",
            "description": "综合验证对Zenodo研究数据的完整枚举、文件体积统计与许可证元数据过滤能力。",
            "requires_auth": False,
            "rate_limit_note": "匿名用户60 req/min，提供Token可提升至100 req/min。",
            "config": config,
            "tests": all_results,
        },
    )

    print(f"\n{'=' * 70}")
    print("✓ Zenodo测试完成 (基础 + 元数据增强)")
    print(f"{'=' * 70}\n")

    return all_results


if __name__ == "__main__":
    run()
