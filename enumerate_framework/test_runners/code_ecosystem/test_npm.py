"""NPM API 完整测试 - 基础枚举 + 元数据过滤"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from ..utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行NPM API完整测试

    测试结构：
    - 1个基础问题：列出所有版本
    - 7个高级问题：
      1. 2024年发布的版本（元数据：发布时间）
      2. Major版本 x.0.0（元数据：版本号解析）
      3. 被废弃的版本（元数据：deprecated标记）
      4. 预发布版本（元数据：版本号格式）
      5. 稳定版本（元数据：版本号格式）
      6. 特定维护者发布的版本（元数据：维护者信息）
      7. 包含特定依赖的版本（元数据：依赖信息）
    """
    print_header("测试 NPM API - 基础 + 元数据增强")

    from fetchers.code_ecosystem.npm import NPMFetcher
    fetcher = NPMFetcher()

    # 默认配置 - 使用react作为示例（版本多、有历史）
    config = {
        "packages": ["react"],
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
            print(f"    - {v['version']} ({v['publish_time'][:10] if v['publish_time'] else 'Unknown'})")

        base_result = {
            "question": base_question,
            "total_count": total_count,
            "versions": [
                {
                    "version": v['version'],
                    "publish_time": v['publish_time'][:10] if v['publish_time'] else None
                } for v in versions_with_metadata
            ]
        }

        # ==================== 增强问题 1：2024年发布 ====================
        print(f"\n[增强问题 1/3] 列出2024年发布的所有版本")
        print(f"  说明: 这需要知道每个版本的发布时间")

        versions_2024 = fetcher.filter_by_year(versions_with_metadata, 2024)

        filtered_count = len(versions_2024)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个版本（占比: {percentage:.1f}%）")
        if versions_2024:
            print(f"  版本列表:")
            for v in versions_2024[:10]:  # 显示前10个
                print(f"    - {v['version']} ({v['publish_time'][:10]})")
            if len(versions_2024) > 10:
                print(f"    ... 还有{len(versions_2024) - 10}个版本")

        enhanced_result_1 = {
            "question": f"列出NPM上{package}包在2024年发布的所有版本",
            "filter_type": "year",
            "filter_value": 2024,
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version'],
                    "publish_time": v['publish_time'][:10]
                } for v in versions_2024
            ]
        }

        # ==================== 增强问题 2：Major版本 ====================
        print(f"\n[增强问题 2/3] 列出所有major版本（x.0.0）")
        print(f"  说明: 这需要解析版本号格式")

        major_versions = fetcher.filter_by_major_version(versions_with_metadata)

        filtered_count = len(major_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个major版本（占比: {percentage:.1f}%）")
        if major_versions:
            print(f"  Major版本列表:")
            for v in major_versions:
                print(f"    - {v['version']} ({v['publish_time'][:10] if v['publish_time'] else 'Unknown'})")

        enhanced_result_2 = {
            "question": f"列出NPM上{package}包的所有major版本（x.0.0）",
            "filter_type": "major_version",
            "filter_value": "x.0.0",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version'],
                    "publish_time": v['publish_time'][:10] if v['publish_time'] else None
                } for v in major_versions
            ]
        }

        # ==================== 增强问题 3：被废弃的版本 ====================
        print(f"\n[增强问题 3/3] 列出所有被标记为废弃（deprecated）的版本")
        print(f"  说明: 这需要检查每个版本的deprecated标记")

        deprecated_versions = fetcher.filter_by_deprecated(versions_with_metadata, deprecated=True)

        filtered_count = len(deprecated_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个被废弃的版本（占比: {percentage:.1f}%）")
        if deprecated_versions:
            print(f"  被废弃的版本:")
            for v in deprecated_versions[:5]:
                msg = v.get('deprecated_message', '')
                msg_preview = msg[:50] if isinstance(msg, str) else 'Deprecated'
                print(f"    - {v['version']}: {msg_preview}")
            if len(deprecated_versions) > 5:
                print(f"    ... 还有{len(deprecated_versions) - 5}个")

        enhanced_result_3 = {
            "question": f"列出NPM上{package}包所有被标记为废弃的版本",
            "filter_type": "deprecated",
            "filter_value": True,
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version'],
                    "deprecated_message": v.get('deprecated_message', 'Deprecated')
                } for v in deprecated_versions
            ]
        }

        # ==================== 增强问题 4：预发布版本 ====================
        print(f"\n[增强问题 4/7] 列出所有预发布版本（包含alpha、beta、rc等）")
        print(f"  说明: 这需要解析版本号中的预发布标记")

        prerelease_versions = fetcher.filter_prerelease_versions(versions_with_metadata)

        filtered_count = len(prerelease_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个预发布版本（占比: {percentage:.1f}%）")
        if prerelease_versions:
            print(f"  预发布版本示例:")
            for v in prerelease_versions[:10]:
                print(f"    - {v['version']} ({v['publish_time'][:10] if v['publish_time'] else 'Unknown'})")
            if len(prerelease_versions) > 10:
                print(f"    ... 还有{len(prerelease_versions) - 10}个版本")

        enhanced_result_4 = {
            "question": f"列出NPM上{package}包的所有预发布版本",
            "filter_type": "prerelease",
            "filter_value": "alpha|beta|rc|pre|preview|dev|canary|next",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version'],
                    "publish_time": v['publish_time'][:10] if v['publish_time'] else None
                } for v in prerelease_versions
            ]
        }

        # ==================== 增强问题 5：稳定版本 ====================
        print(f"\n[增强问题 5/7] 列出所有稳定版本（排除预发布版本）")
        print(f"  说明: 这需要过滤掉包含预发布标记的版本")

        stable_versions = fetcher.filter_stable_versions(versions_with_metadata)

        filtered_count = len(stable_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个稳定版本（占比: {percentage:.1f}%）")
        if stable_versions:
            print(f"  稳定版本示例（前5个）:")
            for v in stable_versions[:5]:
                print(f"    - {v['version']} ({v['publish_time'][:10] if v['publish_time'] else 'Unknown'})")

        enhanced_result_5 = {
            "question": f"列出NPM上{package}包的所有稳定版本",
            "filter_type": "stable",
            "filter_value": "exclude_prerelease",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "versions": [
                {
                    "version": v['version'],
                    "publish_time": v['publish_time'][:10] if v['publish_time'] else None
                } for v in stable_versions[:20]  # 只保存前20个以节省空间
            ]
        }

        # ==================== 增强问题 6：特定维护者 ====================
        print(f"\n[增强问题 6/7] 列出特定维护者发布的版本")
        print(f"  说明: 这需要查询每个版本的维护者信息")

        # 获取第一个版本的第一个维护者作为测试对象
        test_maintainer = None
        if versions_with_metadata and versions_with_metadata[0].get('maintainers'):
            test_maintainer = versions_with_metadata[0]['maintainers'][0]

        if test_maintainer:
            maintainer_versions = fetcher.filter_by_maintainer(versions_with_metadata, test_maintainer)

            filtered_count = len(maintainer_versions)
            percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

            print(f"  ✓ 找到 {filtered_count} 个由 '{test_maintainer}' 发布的版本（占比: {percentage:.1f}%）")
            if maintainer_versions:
                print(f"  版本示例（前5个）:")
                for v in maintainer_versions[:5]:
                    print(f"    - {v['version']} ({v['publish_time'][:10] if v['publish_time'] else 'Unknown'})")

            enhanced_result_6 = {
                "question": f"列出NPM上{package}包由'{test_maintainer}'发布的所有版本",
                "filter_type": "maintainer",
                "filter_value": test_maintainer,
                "total_count": filtered_count,
                "percentage": f"{percentage:.1f}%",
                "versions": [
                    {
                        "version": v['version'],
                        "publish_time": v['publish_time'][:10] if v['publish_time'] else None,
                        "maintainers": v.get('maintainers', [])
                    } for v in maintainer_versions[:20]
                ]
            }
        else:
            print(f"  ⚠ 未找到维护者信息，跳过此测试")
            enhanced_result_6 = {
                "question": f"列出NPM上{package}包由特定维护者发布的所有版本",
                "filter_type": "maintainer",
                "filter_value": None,
                "total_count": 0,
                "percentage": "0%",
                "note": "No maintainer information available"
            }

        # ==================== 增强问题 7：包含特定依赖 ====================
        print(f"\n[增强问题 7/7] 列出包含特定依赖的版本")
        print(f"  说明: 这需要检查每个版本的依赖列表")

        # 寻找一个常见的依赖作为测试对象
        test_dependency = None
        dependency_counts = {}

        for v in versions_with_metadata:
            if v.get('dependencies'):
                for dep in v['dependencies'].keys():
                    dependency_counts[dep] = dependency_counts.get(dep, 0) + 1

        # 选择出现频率最高但不是所有版本都有的依赖
        if dependency_counts:
            sorted_deps = sorted(dependency_counts.items(), key=lambda x: x[1], reverse=True)
            for dep, count in sorted_deps:
                if count < total_count * 0.9:  # 不超过90%的版本都有
                    test_dependency = dep
                    break

        if test_dependency:
            dependency_versions = fetcher.filter_by_dependency(versions_with_metadata, test_dependency)

            filtered_count = len(dependency_versions)
            percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

            print(f"  ✓ 找到 {filtered_count} 个包含依赖'{test_dependency}'的版本（占比: {percentage:.1f}%）")
            if dependency_versions:
                print(f"  版本示例（前5个）:")
                for v in dependency_versions[:5]:
                    dep_version = v.get('dependencies', {}).get(test_dependency, 'N/A')
                    print(f"    - {v['version']}: {test_dependency}@{dep_version}")

            enhanced_result_7 = {
                "question": f"列出NPM上{package}包中包含依赖'{test_dependency}'的所有版本",
                "filter_type": "dependency",
                "filter_value": test_dependency,
                "total_count": filtered_count,
                "percentage": f"{percentage:.1f}%",
                "versions": [
                    {
                        "version": v['version'],
                        "dependency_version": v.get('dependencies', {}).get(test_dependency, 'N/A')
                    } for v in dependency_versions[:20]
                ]
            }
        else:
            print(f"  ⚠ 未找到合适的依赖进行测试，跳过此测试")
            enhanced_result_7 = {
                "question": f"列出NPM上{package}包中包含特定依赖的所有版本",
                "filter_type": "dependency",
                "filter_value": None,
                "total_count": 0,
                "percentage": "0%",
                "note": "No suitable dependency found for testing"
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
                enhanced_result_5,
                enhanced_result_6,
                enhanced_result_7
            ],
            "api_info": api_info,
            "summary": {
                "total_versions": total_count,
                "versions_2024": len(versions_2024),
                "major_versions": len(major_versions),
                "deprecated_versions": len(deprecated_versions),
                "prerelease_versions": len(prerelease_versions),
                "stable_versions": len(stable_versions),
                "maintainer_filter": test_maintainer,
                "dependency_filter": test_dependency
            }
        }

        all_results.append(package_result)

    # 保存结果
    save_result("code_ecosystem/npm", {
        "api_name": "NPM",
        "description": "测试AI的深度枚举能力：不仅要列举所有版本，还要根据元数据过滤",
        "requires_auth": False,
        "difficulty_level": "Advanced (Level 2)",
        "config": config,
        "tests": all_results
    })

    print(f"\n{'='*70}")
    print(f"✓ NPM测试完成!")
    print(f"{'='*70}")
    print(f"\n结果已保存: output/api_tests/code_ecosystem/npm.json")

    return all_results


if __name__ == "__main__":
    run()
