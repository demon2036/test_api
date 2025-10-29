"""CRAN API 完整测试 - 基础枚举 + 预发布版本过滤"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from ..utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行CRAN API完整测试

    测试结构：
    - 1个基础问题：列出所有版本
    - 2个高级问题：
      1. 预发布版本（alpha, beta, rc等）
      2. 稳定版本（排除预发布）
    """
    print_header("测试 CRAN API - 基础 + 预发布版本过滤")

    from fetchers.code_ecosystem.cran import CRANFetcher
    fetcher = CRANFetcher()

    # 默认配置
    config = {
        "packages": ["ggplot2"],
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    all_results = []

    for package in config["packages"]:
        print(f"\n{'='*70}")
        print(f"测试包: {package}")
        print(f"{'='*70}")

        # ==================== 基础问题 ====================
        print(f"\n[基础问题] 列出所有版本")
        versions_with_metadata, api_info, base_question = fetcher.fetch_with_metadata(package=package)

        total_count = len(versions_with_metadata)
        print(f"  ✓ 找到 {total_count} 个版本")
        print(f"  前5个版本:")
        for v in versions_with_metadata[:5]:
            print(f"    - {v['version']} ({v.get('date', 'Unknown')})")

        # ==================== 增强问题 1：预发布版本 ====================
        print(f"\n[增强问题 1/2] 列出所有预发布版本（包含alpha、beta、rc等）")

        prerelease_versions = fetcher.filter_prerelease_versions(versions_with_metadata)

        filtered_count = len(prerelease_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个预发布版本（占比: {percentage:.1f}%）")
        if prerelease_versions:
            print(f"  预发布版本示例:")
            for v in prerelease_versions[:10]:
                print(f"    - {v['version']}")

        # ==================== 增强问题 2：稳定版本 ====================
        print(f"\n[增强问题 2/2] 列出所有稳定版本（排除预发布版本）")

        stable_versions = fetcher.filter_stable_versions(versions_with_metadata)

        filtered_count = len(stable_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个稳定版本（占比: {percentage:.1f}%）")
        if stable_versions:
            print(f"  稳定版本示例（最新5个）:")
            for v in stable_versions[-5:]:
                print(f"    - {v['version']} ({v.get('date', 'Unknown')})")

        # ==================== 汇总结果 ====================
        package_result = {
            "package": package,
            "total_versions": total_count,
            "prerelease_versions": len(prerelease_versions),
            "stable_versions": len(stable_versions),
            "api_info": api_info
        }

        all_results.append(package_result)

    # 保存结果
    save_result("code_ecosystem/cran", {
        "api_name": "CRAN",
        "description": "测试AI的深度枚举能力：识别预发布和稳定版本",
        "requires_auth": False,
        "config": config,
        "tests": all_results
    })

    print(f"\n{'='*70}")
    print(f"✓ CRAN测试完成!")
    print(f"{'='*70}")
    print(f"\n结果已保存: output/api_tests/code_ecosystem/cran.json")

    return all_results


if __name__ == "__main__":
    run()
