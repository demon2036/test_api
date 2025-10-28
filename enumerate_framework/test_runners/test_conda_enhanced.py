"""Conda API 增强测试 - 元数据过滤"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行Conda API增强测试

    测试结构：
    - 1个基础问题：列出所有版本
    - 2个增强问题：
      1. 预发布版本（rc等）
      2. 稳定版本（排除预发布）
    """
    print_header("测试 Conda API - 基础 + 元数据增强")

    from fetchers.conda import CondaFetcher
    fetcher = CondaFetcher()

    # 默认配置
    config = {
        "packages": ["numpy"],
        "channel": "conda-forge"
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    all_results = []

    for package in config["packages"]:
        print(f"\n{'='*70}")
        print(f"测试包: {package} (channel: {config['channel']})")
        print(f"{'='*70}")

        # ==================== 基础问题 ====================
        print(f"\n[基础问题] 列出所有版本")
        versions_with_metadata, api_info, base_question = fetcher.fetch_with_metadata(
            package=package,
            channel=config["channel"]
        )

        total_count = len(versions_with_metadata)
        print(f"  ✓ 找到 {total_count} 个版本")
        print(f"  前5个版本:")
        for v in versions_with_metadata[:5]:
            print(f"    - {v['version']}")

        base_result = {
            "question": base_question,
            "total_count": total_count,
            "versions": [
                {
                    "version": v['version']
                } for v in versions_with_metadata
            ]
        }

        # ==================== 增强问题 1：预发布版本 ====================
        print(f"\n[增强问题 1/2] 列出所有预发布版本（包含rc等）")
        print(f"  说明: 这需要解析版本号中的预发布标记")

        prerelease_versions = fetcher.filter_prerelease_versions(versions_with_metadata)

        filtered_count = len(prerelease_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个预发布版本（占比: {percentage:.1f}%）")
        if prerelease_versions:
            print(f"  预发布版本示例:")
            for v in prerelease_versions[:10]:
                print(f"    - {v['version']}")

        enhanced_result_1 = {
            "question": f"列出Conda上{package}包的所有预发布版本",
            "filter_type": "prerelease",
            "filter_value": "rc|alpha|beta|dev",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version']
                } for v in prerelease_versions
            ]
        }

        # ==================== 增强问题 2：稳定版本 ====================
        print(f"\n[增强问题 2/2] 列出所有稳定版本（排除预发布版本）")
        print(f"  说明: 这需要过滤掉包含预发布标记的版本")

        stable_versions = fetcher.filter_stable_versions(versions_with_metadata)

        filtered_count = len(stable_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个稳定版本（占比: {percentage:.1f}%）")
        if stable_versions:
            print(f"  稳定版本示例（最新5个）:")
            for v in stable_versions[-5:]:
                print(f"    - {v['version']}")

        enhanced_result_2 = {
            "question": f"列出Conda上{package}包的所有稳定版本",
            "filter_type": "stable",
            "filter_value": "exclude_prerelease",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version']
                } for v in stable_versions[:20]  # 只保存前20个以节省空间
            ]
        }

        # ==================== 汇总结果 ====================
        package_result = {
            "package": package,
            "channel": config["channel"],
            "base_test": base_result,
            "enhanced_tests": [
                enhanced_result_1,
                enhanced_result_2
            ],
            "api_info": api_info,
            "summary": {
                "total_versions": total_count,
                "prerelease_versions": len(prerelease_versions),
                "stable_versions": len(stable_versions)
            }
        }

        all_results.append(package_result)

    # 保存结果
    save_result("conda_enhanced", {
        "api_name": "Conda (Enhanced with Metadata Filtering)",
        "description": "测试AI的深度枚举能力：识别预发布和稳定版本",
        "requires_auth": False,
        "difficulty_level": "Advanced (Level 2)",
        "config": config,
        "tests": all_results
    })

    print(f"\n{'='*70}")
    print(f"✓ Conda增强测试完成!")
    print(f"{'='*70}")
    print(f"\n结果已保存: output/api_tests/conda_enhanced.json")

    return all_results


if __name__ == "__main__":
    run()
