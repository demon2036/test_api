"""PyPI API 增强测试 - 元数据过滤"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行PyPI API增强测试

    测试结构：
    - 1个基础问题：列出所有版本
    - 5个增强问题：
      1. 2024年发布的版本（元数据：上传时间）
      2. 包含wheel文件的版本（元数据：文件类型）
      3. 被撤回的版本（元数据：yanked标记）
      4. 预发布版本（alpha, beta, rc等）
      5. 稳定版本（排除预发布）
    """
    print_header("测试 PyPI API - 基础 + 元数据增强")

    from fetchers.pypi import PyPIFetcher
    fetcher = PyPIFetcher()

    # 默认配置 - 使用requests作为示例（有更多预发布版本）
    config = {
        "packages": ["requests"],
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
            wheel_indicator = "🔧" if v['has_wheel'] else "📦"
            print(f"    - {v['version']} {wheel_indicator} ({v['upload_time'][:10] if v['upload_time'] else 'Unknown'})")

        base_result = {
            "question": base_question,
            "total_count": total_count,
            "versions": [
                {
                    "version": v['version'],
                    "upload_time": v['upload_time'][:10] if v['upload_time'] else None
                } for v in versions_with_metadata
            ]
        }

        # ==================== 增强问题 1：2024年发布 ====================
        print(f"\n[增强问题 1/5] 列出2024年发布的所有版本")
        print(f"  说明: 这需要知道每个版本的上传时间")

        versions_2024 = fetcher.filter_by_year(versions_with_metadata, 2024)

        filtered_count = len(versions_2024)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个版本（占比: {percentage:.1f}%）")
        if versions_2024:
            print(f"  版本列表:")
            for v in versions_2024[:10]:
                print(f"    - {v['version']} ({v['upload_time'][:10]})")
            if len(versions_2024) > 10:
                print(f"    ... 还有{len(versions_2024) - 10}个版本")

        enhanced_result_1 = {
            "question": f"列出PyPI上{package}包在2024年发布的所有版本",
            "filter_type": "year",
            "filter_value": 2024,
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version'],
                    "upload_time": v['upload_time'][:10]
                } for v in versions_2024
            ]
        }

        # ==================== 增强问题 2：包含wheel文件 ====================
        print(f"\n[增强问题 2/5] 列出所有包含wheel文件的版本")
        print(f"  说明: 这需要检查每个版本的文件类型")

        wheel_versions = fetcher.filter_by_wheel(versions_with_metadata, has_wheel=True)

        filtered_count = len(wheel_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个版本（占比: {percentage:.1f}%）")
        if wheel_versions:
            print(f"  前5个有wheel的版本:")
            for v in wheel_versions[:5]:
                print(f"    - {v['version']} (文件数: {v['file_count']})")

        enhanced_result_2 = {
            "question": f"列出PyPI上{package}包所有包含wheel文件的版本",
            "filter_type": "has_wheel",
            "filter_value": True,
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version'],
                    "file_count": v['file_count']
                } for v in wheel_versions
            ]
        }

        # ==================== 增强问题 3：被撤回的版本 ====================
        print(f"\n[增强问题 3/5] 列出所有被撤回（yanked）的版本")
        print(f"  说明: 这需要检查每个版本的yanked标记")

        yanked_versions = fetcher.filter_by_yanked(versions_with_metadata, yanked=True)

        filtered_count = len(yanked_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个被撤回的版本（占比: {percentage:.1f}%）")
        if yanked_versions:
            print(f"  被撤回的版本:")
            for v in yanked_versions[:5]:
                print(f"    - {v['version']}")
            if len(yanked_versions) > 5:
                print(f"    ... 还有{len(yanked_versions) - 5}个")

        enhanced_result_3 = {
            "question": f"列出PyPI上{package}包所有被撤回的版本",
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

        # ==================== 增强问题 4：预发布版本 ====================
        print(f"\n[增强问题 4/5] 列出所有预发布版本（包含alpha、beta、rc等）")
        print(f"  说明: 这需要解析版本号中的预发布标记")

        prerelease_versions = fetcher.filter_prerelease_versions(versions_with_metadata)

        filtered_count = len(prerelease_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个预发布版本（占比: {percentage:.1f}%）")
        if prerelease_versions:
            print(f"  预发布版本示例:")
            for v in prerelease_versions[:10]:
                print(f"    - {v['version']} ({v['upload_time'][:10] if v['upload_time'] else 'Unknown'})")
            if len(prerelease_versions) > 10:
                print(f"    ... 还有{len(prerelease_versions) - 10}个版本")

        enhanced_result_4 = {
            "question": f"列出PyPI上{package}包的所有预发布版本",
            "filter_type": "prerelease",
            "filter_value": "alpha|beta|rc|dev|pre|preview",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version'],
                    "upload_time": v['upload_time'][:10] if v['upload_time'] else None
                } for v in prerelease_versions
            ]
        }

        # ==================== 增强问题 5：稳定版本 ====================
        print(f"\n[增强问题 5/5] 列出所有稳定版本（排除预发布版本）")
        print(f"  说明: 这需要过滤掉包含预发布标记的版本")

        stable_versions = fetcher.filter_stable_versions(versions_with_metadata)

        filtered_count = len(stable_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个稳定版本（占比: {percentage:.1f}%）")
        if stable_versions:
            print(f"  稳定版本示例（前5个）:")
            for v in stable_versions[:5]:
                print(f"    - {v['version']} ({v['upload_time'][:10] if v['upload_time'] else 'Unknown'})")

        enhanced_result_5 = {
            "question": f"列出PyPI上{package}包的所有稳定版本",
            "filter_type": "stable",
            "filter_value": "exclude_prerelease",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version'],
                    "upload_time": v['upload_time'][:10] if v['upload_time'] else None
                } for v in stable_versions[:20]  # 只保存前20个以节省空间
            ]
        }

        # ==================== 汇总结果 ====================
        package_result = {
            "package": package,
            "base_test": base_result,
            "enhanced_tests": [
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
    save_result("pypi_enhanced", {
        "api_name": "PyPI (Enhanced with Metadata Filtering)",
        "description": "测试AI的深度枚举能力：不仅要列举所有版本，还要根据元数据过滤",
        "requires_auth": False,
        "difficulty_level": "Advanced (Level 2)",
        "config": config,
        "tests": all_results
    })

    print(f"\n{'='*70}")
    print(f"✓ PyPI增强测试完成!")
    print(f"{'='*70}")
    print(f"\n结果已保存: output/api_tests/pypi_enhanced.json")

    return all_results


if __name__ == "__main__":
    run()
