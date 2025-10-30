"""Go Proxy API 完整测试 - 基础枚举 + 元数据过滤"""

import sys
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


def _format_go_version(version):
    """Standardized answer payload for Go module versions."""
    version_time = version.get('time')
    formatted_time = version_time[:10] if isinstance(version_time, str) and version_time else None
    return {
        "answer": version.get('version', ''),
        "time": formatted_time,
        "module_path": version.get('module_path'),
        "checksum": version.get('checksum')
    }


def run(test_config=None):
    """运行Go Proxy API完整测试

    测试结构：
    - 1个基础问题：列出所有版本
    - 2个高级问题：
      1. 预发布版本（alpha, beta, rc等）
      2. 稳定版本（排除预发布）
    """
    print_header("测试 Go Proxy API - 基础 + 元数据增强")

    from fetchers.code_ecosystem.go_proxy import GoProxyFetcher
    fetcher = GoProxyFetcher()

    # 加载配置（从test_configs）
    default_config = load_package_config("go_proxy", extended=test_config and test_config.get("extended", False))
    config = merge_test_config(default_config, test_config)

    all_results = []

    for module in config["packages"]:
        print(f"\n{'='*70}")
        print(f"测试模块: {module}")
        print(f"{'='*70}")

        # ==================== 基础问题 ====================
        print(f"\n[基础问题] 列出所有版本")
        versions_with_metadata, api_info, base_question = fetcher.fetch_with_metadata(module=module)

        total_count = len(versions_with_metadata)
        print(f"  ✓ 找到 {total_count} 个版本")
        print(f"  前5个版本:")
        for v in versions_with_metadata[:5]:
            print(f"    - {v['version']} ({v.get('time', 'Unknown')[:10] if v.get('time') else 'Unknown'})")

        base_result = build_base_result(
            question=base_question,
            versions=[_format_go_version(v) for v in versions_with_metadata],
            package=module,
            ecosystem="Go Proxy",
            query_category="base_enumeration"
        )

        # ==================== 增强问题 1：预发布版本 ====================
        print(f"\n[增强问题 1/2] 列出所有预发布版本（包含alpha、beta、rc等）")
        print(f"  说明: 这需要解析版本号中的预发布标记")

        prerelease_versions = fetcher.filter_prerelease_versions(versions_with_metadata)

        filtered_count = len(prerelease_versions)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个预发布版本（占比: {percentage:.1f}%）")
        if prerelease_versions:
            print(f"  预发布版本示例:")
            for v in prerelease_versions[:10]:
                print(f"    - {v['version']}")

        enhanced_result_1 = build_enhanced_result(
            question=f"列出Go Proxy上{module}模块的所有预发布版本",
            filtered_versions=prerelease_versions,
            format_func=lambda v: {
                **_format_go_version(v),
                "is_prerelease": True
            },
            package=module,
            ecosystem="Go Proxy",
            filter="include_prerelease=True",
            match_percentage=f"{percentage:.1f}%"
        )

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

        enhanced_result_2 = build_enhanced_result(
            question=f"列出Go Proxy上{module}模块的所有稳定版本",
            filtered_versions=stable_versions,
            format_func=lambda v: {
                **_format_go_version(v),
                "is_prerelease": False
            },
            package=module,
            ecosystem="Go Proxy",
            filter="exclude_prerelease=True",
            match_percentage=f"{percentage:.1f}%"
        )

        # ==================== 汇总结果 ====================
        module_result = {
            "module": module,
            "tests": [
                base_result,
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

        all_results.append(module_result)

    # 保存结果
    save_result("code_ecosystem/go_proxy", {
        "api_name": "Go Proxy",
        "description": "测试AI的深度枚举能力：识别预发布和稳定版本",
        "requires_auth": False,
        "difficulty_level": "Advanced (Level 2)",
        "config": config,
        "tests": all_results
    })

    print(f"\n{'='*70}")
    print(f"✓ Go Proxy测试完成!")
    print(f"{'='*70}")
    print(f"\n结果已保存: output/api_tests/code_ecosystem/go_proxy.json")

    return all_results


if __name__ == "__main__":
    run()
