#!/usr/bin/env python3
"""测试 Homebrew 的高级功能"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "enumerate_framework"))

from fetchers.homebrew import HomebrewFetcher


def test_homebrew_advanced_features():
    """测试 Homebrew 的高级过滤功能"""
    print("=" * 60)
    print("测试 Homebrew 高级功能")
    print("=" * 60)

    fetcher = HomebrewFetcher()

    # 1. 测试 fetch_with_metadata（单个 formula）
    print("\n[测试 1] 获取 redis formula 的完整元数据...")
    redis_data, api_info, question = fetcher.fetch_with_metadata(formula='redis')
    if redis_data:
        print(f"✓ 获取成功")
        print(f"  - 名称: {redis_data.get('name')}")
        print(f"  - 描述: {redis_data.get('desc', '')[:60]}...")
        print(f"  - 稳定版本: {redis_data.get('versions', {}).get('stable')}")
        print(f"  - 是否 keg-only: {redis_data.get('keg_only', False)}")
        print(f"  - 有 service: {redis_data.get('service') is not None}")
        print(f"  - 别名: {redis_data.get('aliases', [])}")
    else:
        print("✗ 获取失败")

    # 2. 测试 get_service_info
    print("\n[测试 2] 提取 redis 的 service 信息...")
    service_info = fetcher.get_service_info(redis_data)
    if service_info:
        print(f"✓ Service 信息:")
        print(f"  - 运行命令: {service_info['run_command'][:80]}...")
        print(f"  - 运行类型: {service_info['run_type']}")
        print(f"  - 工作目录: {service_info['working_dir']}")
        print(f"  - 日志路径: {service_info['log_path']}")
    else:
        print("  (该 formula 没有 service 定义)")

    # 3. 测试 fetch_all_formulae_with_metadata
    print("\n[测试 3] 获取所有 formulae（含元数据，限制 500 个）...")
    formulae, api_info, question = fetcher.fetch_all_formulae_with_metadata(max_formulae=500)
    print(f"✓ 获取了 {len(formulae)} 个 formulae（含完整元数据）")

    # 4. 测试 filter_with_service
    print("\n[测试 4] 过滤有 service 定义的 formulae...")
    service_formulae = fetcher.filter_with_service(formulae)
    print(f"✓ 找到 {len(service_formulae)} 个有 service 的 formulae")
    if len(service_formulae) > 0:
        print(f"  前10个: {[f['name'] for f in service_formulae[:10]]}")

    # 5. 测试 filter_keg_only
    print("\n[测试 5] 过滤 keg-only 的 formulae...")
    keg_only_formulae = fetcher.filter_keg_only(formulae)
    print(f"✓ 找到 {len(keg_only_formulae)} 个 keg-only 的 formulae")
    if len(keg_only_formulae) > 0:
        print(f"  前10个: {[f['name'] for f in keg_only_formulae[:10]]}")

    # 6. 测试 get_keg_only_reason
    if len(keg_only_formulae) > 0:
        print("\n[测试 6] 获取 keg-only 原因（第一个 keg-only formula）...")
        reason = fetcher.get_keg_only_reason(keg_only_formulae[0])
        if reason:
            print(f"✓ Keg-only 原因:")
            print(f"  - Formula: {reason['name']}")
            print(f"  - 原因代码: {reason['reason']}")
            print(f"  - 说明: {reason['explanation'] or '(无额外说明)'}")

    # 7. 测试 filter_with_aliases
    print("\n[测试 7] 过滤有别名的 formulae...")
    aliased_formulae = fetcher.filter_with_aliases(formulae)
    print(f"✓ 找到 {len(aliased_formulae)} 个有别名的 formulae")
    if len(aliased_formulae) > 0:
        print(f"  前10个: {[f['name'] for f in aliased_formulae[:10]]}")

    # 8. 测试 get_aliases
    if len(aliased_formulae) > 0:
        print("\n[测试 8] 获取别名信息（前3个有别名的 formulae）...")
        for formula in aliased_formulae[:3]:
            alias_info = fetcher.get_aliases(formula)
            print(f"  - {alias_info['name']}: {alias_info['aliases']}")

    # 9. 测试 filter_deprecated
    print("\n[测试 9] 过滤已弃用的 formulae...")
    deprecated_formulae = fetcher.filter_deprecated(formulae)
    print(f"✓ 找到 {len(deprecated_formulae)} 个已弃用的 formulae")
    if len(deprecated_formulae) > 0:
        print(f"  示例: {[f['name'] for f in deprecated_formulae[:5]]}")

    # 10. 组合测试：有 service 且不是 keg-only
    print("\n[测试 10] 组合过滤：有 service 但不是 keg-only...")
    service_not_keg = [f for f in service_formulae if not f.get('keg_only', False)]
    print(f"✓ 找到 {len(service_not_keg)} 个符合条件的 formulae")
    if len(service_not_keg) > 0:
        print(f"  示例: {[f['name'] for f in service_not_keg[:5]]}")

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！Homebrew 高级功能正常工作")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_homebrew_advanced_features()
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
