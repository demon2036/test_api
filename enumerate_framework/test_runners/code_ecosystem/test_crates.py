"""Crates.io API 完整测试 - 基础枚举 + 元数据过滤"""

import sys
import time
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from ..utils import save_result, create_test_result, print_header


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

    # 默认配置
    config = {
        "crates": ["serde"],
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    all_results = []

    for crate in config["crates"]:
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

        base_result = {
            "question": base_question,
            "total_count": total_count,
            "versions": [
                {
                    "version": v['version'],
                    "created_at": v['created_at'][:10] if v.get('created_at') else None
                } for v in versions_with_metadata
            ]
        }

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

        enhanced_result_1 = {
            "question": f"列出Crates.io上{crate}包在2024年发布的所有版本",
            "filter_type": "year",
            "filter_value": 2024,
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version'],
                    "created_at": v['created_at'][:10]
                } for v in versions_2024
            ]
        }

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

        enhanced_result_2 = {
            "question": f"列出Crates.io上{crate}包所有被撤回的版本",
            "filter_type": "yanked",
            "filter_value": True,
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version']
                } for v in yanked_versions
            ]
        }

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

        enhanced_result_3 = {
            "question": f"列出Crates.io上{crate}包的所有预发布版本",
            "filter_type": "prerelease",
            "filter_value": "alpha|beta|rc|pre",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version'],
                    "created_at": v['created_at'][:10] if v.get('created_at') else None
                } for v in prerelease_versions
            ]
        }

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

        enhanced_result_4 = {
            "question": f"列出Crates.io上{crate}包的所有稳定版本",
            "filter_type": "stable",
            "filter_value": "exclude_prerelease",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version'],
                    "created_at": v['created_at'][:10] if v.get('created_at') else None
                } for v in stable_versions[:20]  # 只保存前20个以节省空间
            ]
        }

        # ==================== 汇总结果 ====================
        crate_result = {
            "crate": crate,
            "base_test": base_result,
            "enhanced_tests": [
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
