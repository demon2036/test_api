"""Zenodo API 增强测试 - 元数据过滤"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行Zenodo API增强测试

    测试结构：
    - 1个基础问题：列出所有记录
    - 3个增强问题：
      1. 大于1GB的数据集（元数据：文件大小）
      2. Software类型的记录（元数据：资源类型）
      3. Creative Commons许可的记录（元数据：许可证）
    """
    print_header("测试 Zenodo API - 基础 + 元数据增强")

    from fetchers.zenodo import ZenodoFetcher
    fetcher = ZenodoFetcher()

    # 默认配置 - 使用有足够数据的ORCID
    config = {
        "researchers": [
            {"orcid": "0000-0002-1825-0097", "name": "Joanna Rees"},
        ],
        "max_records": 100
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    all_results = []

    for researcher in config["researchers"]:
        orcid = researcher["orcid"]
        name = researcher["name"]

        print(f"\n{'='*70}")
        print(f"测试研究者: {name} (ORCID: {orcid})")
        print(f"{'='*70}")

        # ==================== 基础问题 ====================
        print(f"\n[基础问题] 列出所有记录")
        records_with_metadata, api_info, base_question = fetcher.fetch_by_orcid_with_metadata(
            orcid=orcid,
            max_records=config["max_records"]
        )

        total_count = len(records_with_metadata)
        print(f"  ✓ 找到 {total_count} 条记录")
        print(f"  前3条:")
        for record in records_with_metadata[:3]:
            title = record.get('title', 'Unknown')[:70]
            pub_date = record.get('publication_date', 'N/A')
            res_type = record.get('resource_type', 'unknown')
            print(f"    - [{pub_date}] [{res_type}] {title}...")

        # 保存基础结果
        base_result = {
            "question": base_question,
            "total_count": total_count,
            "records": [
                {
                    "doi": r.get('doi'),
                    "title": r.get('title'),
                    "publication_date": r.get('publication_date'),
                    "resource_type": r.get('resource_type'),
                    "total_size_bytes": r.get('total_size_bytes'),
                    "license": r.get('license')
                } for r in records_with_metadata
            ],
            "metadata_available": True
        }

        # ==================== 增强问题 1：大文件 (>1GB) ====================
        print(f"\n[增强问题 1/3] 列出所有大于1GB的数据集")
        print(f"  说明: 这需要知道每条记录的文件大小")

        large_records = fetcher.filter_by_size(records_with_metadata, min_size_gb=1.0)

        filtered_count = len(large_records)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 条（占比: {percentage:.1f}%）")
        print(f"  前3条:")
        for record in large_records[:3]:
            title = record.get('title', 'Unknown')[:60]
            size_gb = record.get('total_size_bytes', 0) / (1024**3)
            res_type = record.get('resource_type', 'unknown')
            print(f"    - [{res_type}] {title}...")
            print(f"      大小: {size_gb:.2f} GB")

        # 统计总大小
        total_size_gb = sum(r.get('total_size_bytes', 0) for r in large_records) / (1024**3)

        enhanced_result_1 = {
            "question": f"列出Zenodo中{name} (ORCID: {orcid})的所有大于1GB的数据集",
            "filter_type": "size",
            "filter_value": "1GB",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "total_size_gb": f"{total_size_gb:.2f}",
            "records": [
                {
                    "doi": r.get('doi'),
                    "title": r.get('title'),
                    "size_gb": f"{r.get('total_size_bytes', 0) / (1024**3):.2f}",
                    "resource_type": r.get('resource_type'),
                    "publication_date": r.get('publication_date')
                } for r in large_records
            ]
        }

        # ==================== 增强问题 2：Software类型 ====================
        print(f"\n[增强问题 2/3] 列出所有Software类型的记录")
        print(f"  说明: 这需要知道每条记录的资源类型（dataset, software, publication等）")

        software_records = fetcher.filter_by_resource_type(records_with_metadata, "software")

        filtered_count = len(software_records)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 条（占比: {percentage:.1f}%）")
        print(f"  前3条:")
        for record in software_records[:3]:
            title = record.get('title', 'Unknown')[:70]
            version = record.get('version', 'N/A')
            pub_date = record.get('publication_date', 'N/A')
            print(f"    - [{pub_date}] {title}...")
            print(f"      版本: {version}")

        # 统计资源类型分布
        from collections import Counter
        type_counts = Counter()
        for record in records_with_metadata:
            res_type = record.get('resource_type', 'unknown')
            type_counts[res_type] += 1

        print(f"  资源类型分布:")
        for res_type, count in type_counts.most_common(5):
            print(f"    {res_type}: {count}条")

        enhanced_result_2 = {
            "question": f"列出Zenodo中{name} (ORCID: {orcid})的所有Software类型记录",
            "filter_type": "resource_type",
            "filter_value": "software",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "resource_type_distribution": dict(type_counts),
            "records": [
                {
                    "doi": r.get('doi'),
                    "title": r.get('title'),
                    "version": r.get('version'),
                    "publication_date": r.get('publication_date'),
                    "license": r.get('license')
                } for r in software_records
            ]
        }

        # ==================== 增强问题 3：Creative Commons许可 ====================
        print(f"\n[增强问题 3/3] 列出所有使用Creative Commons许可的记录")
        print(f"  说明: 这需要知道每条记录的许可证信息")

        cc_records = fetcher.filter_by_license(records_with_metadata, "cc")

        filtered_count = len(cc_records)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 条（占比: {percentage:.1f}%）")
        print(f"  前3条:")
        for record in cc_records[:3]:
            title = record.get('title', 'Unknown')[:70]
            license_id = record.get('license', 'unknown')
            pub_date = record.get('publication_date', 'N/A')
            print(f"    - [{pub_date}] {title}...")
            print(f"      许可证: {license_id}")

        # 统计许可证分布
        license_counts = Counter()
        for record in records_with_metadata:
            license_id = record.get('license', 'unknown')
            license_counts[license_id] += 1

        print(f"  许可证分布:")
        for license_id, count in license_counts.most_common():
            print(f"    {license_id}: {count}条")

        enhanced_result_3 = {
            "question": f"列出Zenodo中{name} (ORCID: {orcid})的所有使用Creative Commons许可的记录",
            "filter_type": "license",
            "filter_value": "cc",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "license_distribution": dict(license_counts),
            "records": [
                {
                    "doi": r.get('doi'),
                    "title": r.get('title'),
                    "license": r.get('license'),
                    "resource_type": r.get('resource_type'),
                    "publication_date": r.get('publication_date')
                } for r in cc_records
            ]
        }

        # ==================== 汇总结果 ====================
        researcher_result = {
            "researcher": name,
            "orcid": orcid,
            "base_test": base_result,
            "enhanced_tests": [
                enhanced_result_1,
                enhanced_result_2,
                enhanced_result_3
            ],
            "api_info": api_info,
            "summary": {
                "total_records": total_count,
                "large_datasets": len(large_records),
                "software_records": len(software_records),
                "cc_licensed": len(cc_records),
                "resource_types": dict(type_counts),
                "licenses": dict(license_counts)
            }
        }

        all_results.append(researcher_result)

    # 保存结果
    save_result("zenodo_enhanced", {
        "api_name": "Zenodo (Enhanced with Metadata Filtering)",
        "description": "测试AI的深度枚举能力：不仅要列举所有项目，还要根据元数据过滤",
        "requires_auth": False,
        "difficulty_level": "Advanced (Level 2)",
        "config": config,
        "tests": all_results
    })

    print(f"\n{'='*70}")
    print(f"✓ Zenodo增强测试完成!")
    print(f"{'='*70}")
    print(f"\n测试难度提升：")
    print(f"  Level 1 (基础): 列举所有记录")
    print(f"  Level 2 (增强): 列举并过滤 - 需要理解每条记录的详细元数据")
    print(f"\n结果已保存: output/api_tests/zenodo_enhanced.json")

    return all_results


if __name__ == "__main__":
    run()
