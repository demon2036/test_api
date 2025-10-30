"""PyPI API 完整测试 - 基础枚举 + 元数据过滤"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
    from test_runners.code_ecosystem.code_utils import (
        load_package_config, merge_test_config, print_section_header,
        print_test_header, print_filter_stats, print_version_preview,
        build_base_result, build_enhanced_result, format_version_basic,
        run_year_filter_test, run_prerelease_filter_test, run_stable_filter_test
    )
else:
    from ..utils import save_result, create_test_result, print_header
    from .code_utils import (
        load_package_config, merge_test_config, print_section_header,
        print_test_header, print_filter_stats, print_version_preview,
        build_base_result, build_enhanced_result, format_version_basic,
        run_year_filter_test, run_prerelease_filter_test, run_stable_filter_test
    )


def run(test_config=None):
    """运行PyPI API完整测试

    测试结构：
    - 1个基础问题：列出所有版本
    - 5个高级问题：
      1. 2024年发布的版本（元数据：上传时间）
      2. 包含wheel文件的版本（元数据：文件类型）
      3. 被撤回的版本（元数据：yanked标记）
      4. 预发布版本（alpha, beta, rc等）
      5. 稳定版本（排除预发布）
    """
    print_header("测试 PyPI API - 基础 + 元数据增强")

    from fetchers.code_ecosystem.pypi import PyPIFetcher
    fetcher = PyPIFetcher()

    # 加载配置 - 支持extended模式加载django等额外包
    default_config = load_package_config("pypi", extended=test_config and test_config.get("extended", False))
    config = merge_test_config(default_config, test_config)

    all_results = []

    for package in config["packages"]:
        print_section_header("测试包", package)

        # ==================== 基础问题 ====================
        print(f"\n[基础问题] 列出所有版本")
        versions_with_metadata, api_info, base_question = fetcher.fetch_with_metadata(package=package)

        total_count = len(versions_with_metadata)
        print(f"  ✓ 找到 {total_count} 个版本")
        print(f"  前5个版本:")
        for v in versions_with_metadata[:5]:
            wheel_indicator = "🔧" if v['has_wheel'] else "📦"
            print(f"    - {v['version']} {wheel_indicator} ({v['upload_time'][:10] if v['upload_time'] else 'Unknown'})")

        base_result = build_base_result(
            question=base_question,
            versions=[format_version_basic(v) for v in versions_with_metadata],
            package=package,
            ecosystem="PyPI",
            query_category="base_enumeration"
        )

        # ==================== 增强问题 1：2024年发布 ====================
        print_test_header(1, 5, "列出2024年发布的所有版本")
        print(f"  说明: 这需要知道每个版本的上传时间")

        enhanced_result_1 = run_year_filter_test(
            fetcher, versions_with_metadata, 2024, package, "PyPI"
        )

        versions_2024 = fetcher.filter_by_year(versions_with_metadata, 2024)
        print_filter_stats(len(versions_2024), total_count)
        if versions_2024:
            print(f"  版本列表:")
            print_version_preview(versions_2024, max_items=10)

        # ==================== 增强问题 2：包含wheel文件 ====================
        print_test_header(2, 5, "列出所有包含wheel文件的版本")
        print(f"  说明: 这需要检查每个版本的文件类型")

        wheel_versions = fetcher.filter_by_wheel(versions_with_metadata, has_wheel=True)

        print_filter_stats(len(wheel_versions), total_count)
        if wheel_versions:
            print(f"  前5个有wheel的版本:")
            for v in wheel_versions[:5]:
                print(f"    - {v['version']} (文件数: {v['file_count']})")

        enhanced_result_2 = build_enhanced_result(
            question=f"列出PyPI上{package}包所有包含wheel文件的版本",
            filtered_versions=wheel_versions,
            format_func=lambda v: {
                "answer": v['version'],
                "file_count": v['file_count'],
                "has_wheel": v.get('has_wheel', False)
            },
            package=package,
            ecosystem="PyPI",
            filter="has_wheel=True"
        )

        # ==================== 增强问题 3：被撤回的版本 ====================
        print_test_header(3, 5, "列出所有被撤回（yanked）的版本")
        print(f"  说明: 这需要检查每个版本的yanked标记")

        yanked_versions = fetcher.filter_by_yanked(versions_with_metadata, yanked=True)

        print_filter_stats(len(yanked_versions), total_count)
        if yanked_versions:
            print(f"  被撤回的版本:")
            print_version_preview(yanked_versions, max_items=5)

        enhanced_result_3 = build_enhanced_result(
            question=f"列出PyPI上{package}包所有被撤回的版本",
            filtered_versions=yanked_versions,
            format_func=lambda v: {
                "answer": v['version'],
                "yanked": True,
                "upload_time": v.get('upload_time', '')[:10] if v.get('upload_time') else None
            },
            package=package,
            ecosystem="PyPI",
            filter="yanked=True"
        )

        # ==================== 增强问题 4：预发布版本 ====================
        print_test_header(4, 5, "列出所有预发布版本（包含alpha、beta、rc等）")
        print(f"  说明: 这需要解析版本号中的预发布标记")

        enhanced_result_4 = run_prerelease_filter_test(
            fetcher, versions_with_metadata, package, "PyPI"
        )

        prerelease_versions = fetcher.filter_prerelease_versions(versions_with_metadata)
        print_filter_stats(len(prerelease_versions), total_count)
        if prerelease_versions:
            print(f"  预发布版本示例:")
            print_version_preview(prerelease_versions, max_items=10)

        # ==================== 增强问题 5：稳定版本 ====================
        print_test_header(5, 5, "列出所有稳定版本（排除预发布版本）")
        print(f"  说明: 这需要过滤掉包含预发布标记的版本")

        enhanced_result_5 = run_stable_filter_test(
            fetcher, versions_with_metadata, package, "PyPI", limit=20
        )

        stable_versions = fetcher.filter_stable_versions(versions_with_metadata)
        print_filter_stats(len(stable_versions), total_count)
        if stable_versions:
            print(f"  稳定版本示例（前5个）:")
            print_version_preview(stable_versions, max_items=5)

        # ==================== 汇总结果 ====================
        package_result = {
            "package": package,
            "tests": [
                base_result,
                enhanced_result_1,
                enhanced_result_2,
                enhanced_result_3,
                enhanced_result_4,
                enhanced_result_5
            ],
            "api_info": api_info,
            "summary": {
                "total_versions": total_count,
                "versions_2024": len(versions_2024),
                "wheel_versions": len(wheel_versions),
                "yanked_versions": len(yanked_versions),
                "prerelease_versions": len(prerelease_versions),
                "stable_versions": len(stable_versions)
            }
        }

        all_results.append(package_result)

    # 保存结果
    save_result("code_ecosystem/pypi", {
        "api_name": "PyPI",
        "description": "测试AI的深度枚举能力：不仅要列举所有版本，还要根据元数据过滤",
        "requires_auth": False,
        "difficulty_level": "Advanced (Level 2)",
        "config": config,
        "tests": all_results
    })

    print_section_header("✓ PyPI测试完成!")
    print(f"\n结果已保存: output/api_tests/code_ecosystem/pypi.json")

    return all_results


if __name__ == "__main__":
    run()
