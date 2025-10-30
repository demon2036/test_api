"""Crates.io API 完整测试 - 基础枚举 + 元数据过滤"""

import sys
import time
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, print_header
    from test_runners.code_ecosystem.code_utils import (
        load_package_config,
        merge_test_config,
        build_base_result,
        build_enhanced_result,
    )
else:
    from ..utils import save_result, print_header
    from .code_utils import (
        load_package_config,
        merge_test_config,
        build_base_result,
        build_enhanced_result,
    )


def _format_crates_version(version):
    """Provide a standardized answer payload for Crates.io versions."""
    created_at = version.get('created_at')
    formatted_date = created_at[:10] if isinstance(created_at, str) and created_at else None
    license_value = version.get('license', '')
    # Some versions use 'num' instead of 'version'
    identifier = version.get('version') or version.get('num', '')
    return {
        "answer": identifier,
        "created_at": formatted_date,
        "downloads": version.get('downloads', 0),
        "yanked": version.get('yanked', False),
        "license": license_value
    }


def run(test_config=None):
    """运行Crates.io API完整测试

    测试结构：
    - 1个基础问题：列出所有版本
    - 4个高级问题：
      1. 2024年发布的版本（元数据：created_at）
      2. 被撤回的版本（元数据：yanked标记）
      3. 预发布版本（alpha, beta, rc等）
      4. 稳定版本（排除预发布）
    """
    print_header("测试 Crates.io API - 基础 + 元数据增强")

    from fetchers.code_ecosystem.crates import CratesFetcher
    fetcher = CratesFetcher()

    # 加载配置（从test_configs）
    default_config = load_package_config("crates", extended=test_config and test_config.get("extended", False))
    config = merge_test_config(default_config, test_config)

    all_results = []

    for crate in config["packages"]:
        print(f"\n{'='*70}")
        print(f"测试crate: {crate}")
        print(f"{'='*70}")

        # ==================== 基础问题 ====================
        print(f"\n[基础问题] 列出所有版本")
        versions_with_metadata, api_info, base_question = fetcher.fetch_with_metadata(crate=crate)

        total_count = len(versions_with_metadata)
        print(f"  ✓ 找到 {total_count} 个版本")
        print(f"  前5个版本:")
        for v in versions_with_metadata[:5]:
            yanked_indicator = "⚠️" if v.get('yanked', False) else "✓"
            print(f"    {yanked_indicator} {v['version']} ({v['created_at'][:10] if v.get('created_at') else 'Unknown'})")

        base_result = build_base_result(
            question=base_question,
            versions=[_format_crates_version(v) for v in versions_with_metadata],
            package=crate,
            ecosystem="Crates.io",
            query_category="base_enumeration"
        )

        # ==================== 增强问题 1：2024年发布 ====================
        print(f"\n[增强问题 1/4] 列出2024年发布的所有版本")
        print(f"  说明: 这需要知道每个版本的创建时间")

        versions_2024 = fetcher.filter_by_year(versions_with_metadata, 2024)

        filtered_count = len(versions_2024)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个版本（占比: {percentage:.1f}%）")
        if versions_2024:
            print(f"  版本列表:")
            for v in versions_2024[:10]:
                print(f"    - {v['version']} ({v['created_at'][:10]})")
            if len(versions_2024) > 10:
                print(f"    ... 还有{len(versions_2024) - 10}个版本")

        enhanced_result_1 = build_enhanced_result(
            question=f"列出Crates.io上{crate}包在2024年发布的所有版本",
            filtered_versions=versions_2024,
            format_func=_format_crates_version,
            package=crate,
            ecosystem="Crates.io",
            filter="year=2024",
            match_percentage=f"{percentage:.1f}%"
        )

        # ==================== 增强问题 2：被撤回的版本 ====================
        print(f"\n[增强问题 2/4] 列出所有被撤回（yanked）的版本")
        print(f"  说明: 这需要检查每个版本的yanked标记")

        yanked_versions = fetcher.filter_by_yanked(versions_with_metadata, yanked=True)

        filtered_count = len(yanked_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个被撤回的版本（占比: {percentage:.1f}%）")
        if yanked_versions:
            print(f"  被撤回的版本:")
            for v in yanked_versions[:10]:
                print(f"    - {v['version']}")
            if len(yanked_versions) > 10:
                print(f"    ... 还有{len(yanked_versions) - 10}个")

        enhanced_result_2 = build_enhanced_result(
            question=f"列出Crates.io上{crate}包所有被撤回的版本",
            filtered_versions=yanked_versions,
            format_func=lambda v: {
                "answer": v.get('version') or v.get('num', ''),
                "created_at": v.get('created_at', '')[:10] if v.get('created_at') else None,
                "downloads": v.get('downloads', 0),
                "yanked": True
            },
            package=crate,
            ecosystem="Crates.io",
            filter="yanked=True",
            match_percentage=f"{percentage:.1f}%"
        )

        # ==================== 增强问题 3：预发布版本 ====================
        print(f"\n[增强问题 3/4] 列出所有预发布版本（包含alpha、beta、rc等）")
        print(f"  说明: 这需要解析版本号中的预发布标记")

        prerelease_versions = fetcher.filter_prerelease_versions(versions_with_metadata)

        filtered_count = len(prerelease_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个预发布版本（占比: {percentage:.1f}%）")
        if prerelease_versions:
            print(f"  预发布版本示例:")
            for v in prerelease_versions[:10]:
                print(f"    - {v['version']}")

        enhanced_result_3 = build_enhanced_result(
            question=f"列出Crates.io上{crate}包的所有预发布版本",
            filtered_versions=prerelease_versions,
            format_func=lambda v: {
                **_format_crates_version(v),
                "is_prerelease": True
            },
            package=crate,
            ecosystem="Crates.io",
            filter="include_prerelease=True",
            match_percentage=f"{percentage:.1f}%"
        )

        # ==================== 增强问题 4：稳定版本 ====================
        print(f"\n[增强问题 4/4] 列出所有稳定版本（排除预发布版本）")
        print(f"  说明: 这需要过滤掉包含预发布标记的版本")

        stable_versions = fetcher.filter_stable_versions(versions_with_metadata)

        filtered_count = len(stable_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个稳定版本（占比: {percentage:.1f}%）")
        if stable_versions:
            print(f"  稳定版本示例（最新5个）:")
            for v in stable_versions[-5:]:
                print(f"    - {v['version']}")

        enhanced_result_4 = build_enhanced_result(
            question=f"列出Crates.io上{crate}包的所有稳定版本",
            filtered_versions=stable_versions,
            format_func=lambda v: {
                **_format_crates_version(v),
                "is_prerelease": False
            },
            package=crate,
            ecosystem="Crates.io",
            filter="exclude_prerelease=True",
            match_percentage=f"{percentage:.1f}%"
        )

        # ==================== 汇总结果 ====================
        crate_result = {
            "crate": crate,
            "tests": [
                base_result,
                enhanced_result_1,
                enhanced_result_2,
                enhanced_result_3,
                enhanced_result_4
            ],
            "api_info": api_info,
            "summary": {
                "total_versions": total_count,
                "versions_2024": len(versions_2024),
                "yanked_versions": len(yanked_versions),
                "prerelease_versions": len(prerelease_versions),
                "stable_versions": len(stable_versions)
            }
        }

        all_results.append(crate_result)

        # 尊重速率限制
        time.sleep(1)

    # 保存结果
    save_result("code_ecosystem/crates", {
        "api_name": "Crates.io",
        "description": "测试AI的深度枚举能力：不仅要列举所有版本，还要根据元数据过滤",
        "requires_auth": False,
        "difficulty_level": "Advanced (Level 2)",
        "config": config,
        "tests": all_results
    })

    print(f"\n{'='*70}")
    print(f"✓ Crates.io测试完成!")
    print(f"{'='*70}")
    print(f"\n结果已保存: output/api_tests/code_ecosystem/crates.json")

    return all_results


if __name__ == "__main__":
    run()
