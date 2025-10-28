#!/usr/bin/env python3
"""
综合测试脚本 - 测试所有增强的包管理器API
测试包括预发布版本过滤等高级功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def test_npm():
    print("\n" + "="*70)
    print("测试 NPM (react)")
    print("="*70)
    from fetchers.npm import NPMFetcher
    fetcher = NPMFetcher()

    versions, api_info, question = fetcher.fetch_with_metadata("react")
    print(f"✓ 总版本数: {len(versions)}")

    prerelease = fetcher.filter_prerelease_versions(versions)
    print(f"✓ 预发布版本: {len(prerelease)}")

    stable = fetcher.filter_stable_versions(versions)
    print(f"✓ 稳定版本: {len(stable)}")

    return len(versions) > 0

def test_pypi():
    print("\n" + "="*70)
    print("测试 PyPI (requests)")
    print("="*70)
    from fetchers.pypi import PyPIFetcher
    fetcher = PyPIFetcher()

    versions, api_info, question = fetcher.fetch_with_metadata("requests")
    print(f"✓ 总版本数: {len(versions)}")

    prerelease = fetcher.filter_prerelease_versions(versions)
    print(f"✓ 预发布版本: {len(prerelease)}")

    stable = fetcher.filter_stable_versions(versions)
    print(f"✓ 稳定版本: {len(stable)}")

    return len(versions) > 0

def test_crates():
    print("\n" + "="*70)
    print("测试 Crates.io (serde)")
    print("="*70)
    from fetchers.crates import CratesFetcher
    import time
    fetcher = CratesFetcher()

    time.sleep(1)  # Rate limiting
    versions, api_info, question = fetcher.fetch_with_metadata("serde")
    print(f"✓ 总版本数: {len(versions)}")

    prerelease = fetcher.filter_prerelease_versions(versions)
    print(f"✓ 预发布版本: {len(prerelease)}")

    stable = fetcher.filter_stable_versions(versions)
    print(f"✓ 稳定版本: {len(stable)}")

    return len(versions) > 0

def test_rubygems():
    print("\n" + "="*70)
    print("测试 RubyGems (rails)")
    print("="*70)
    from fetchers.rubygems import RubyGemsFetcher
    fetcher = RubyGemsFetcher()

    versions, api_info, question = fetcher.fetch_with_metadata("rails")
    print(f"✓ 总版本数: {len(versions)}")

    prerelease = fetcher.filter_prerelease_versions(versions)
    print(f"✓ 预发布版本: {len(prerelease)}")

    stable = fetcher.filter_stable_versions(versions)
    print(f"✓ 稳定版本: {len(stable)}")

    return len(versions) > 0

def test_nuget():
    print("\n" + "="*70)
    print("测试 NuGet (Newtonsoft.Json)")
    print("="*70)
    from fetchers.nuget import NuGetFetcher
    fetcher = NuGetFetcher()

    versions, api_info, question = fetcher.fetch_with_metadata("Newtonsoft.Json")
    print(f"✓ 总版本数: {len(versions)}")

    prerelease = fetcher.filter_prerelease_versions(versions)
    print(f"✓ 预发布版本: {len(prerelease)}")

    stable = fetcher.filter_stable_versions(versions)
    print(f"✓ 稳定版本: {len(stable)}")

    return len(versions) > 0

def test_go_proxy():
    print("\n" + "="*70)
    print("测试 Go Proxy (github.com/gin-gonic/gin)")
    print("="*70)
    from fetchers.go_proxy import GoProxyFetcher
    fetcher = GoProxyFetcher()

    versions, api_info, question = fetcher.fetch_with_metadata("github.com/gin-gonic/gin")
    print(f"✓ 总版本数: {len(versions)}")

    prerelease = fetcher.filter_prerelease_versions(versions)
    print(f"✓ 预发布版本: {len(prerelease)}")

    stable = fetcher.filter_stable_versions(versions)
    print(f"✓ 稳定版本: {len(stable)}")

    return len(versions) > 0

def test_conda():
    print("\n" + "="*70)
    print("测试 Conda (numpy)")
    print("="*70)
    from fetchers.conda import CondaFetcher
    fetcher = CondaFetcher()

    versions, api_info, question = fetcher.fetch_with_metadata("numpy", channel="conda-forge")
    print(f"✓ 总版本数: {len(versions)}")

    prerelease = fetcher.filter_prerelease_versions(versions)
    print(f"✓ 预发布版本: {len(prerelease)}")

    stable = fetcher.filter_stable_versions(versions)
    print(f"✓ 稳定版本: {len(stable)}")

    return len(versions) > 0

def test_cran():
    print("\n" + "="*70)
    print("测试 CRAN (ggplot2)")
    print("="*70)
    from fetchers.cran import CRANFetcher
    fetcher = CRANFetcher()

    versions, api_info, question = fetcher.fetch_with_metadata("ggplot2")
    print(f"✓ 总版本数: {len(versions)}")

    prerelease = fetcher.filter_prerelease_versions(versions)
    print(f"✓ 预发布版本: {len(prerelease)}")

    stable = fetcher.filter_stable_versions(versions)
    print(f"✓ 稳定版本: {len(stable)}")

    return len(versions) > 0

def main():
    print("\n" + "="*70)
    print("开始综合测试所有增强的包管理器API")
    print("="*70)

    tests = [
        ("NPM", test_npm),
        ("PyPI", test_pypi),
        ("Crates.io", test_crates),
        ("RubyGems", test_rubygems),
        ("NuGet", test_nuget),
        ("Go Proxy", test_go_proxy),
        ("Conda", test_conda),
        ("CRAN", test_cran),
    ]

    results = {}

    for name, test_func in tests:
        try:
            success = test_func()
            results[name] = "✓ PASS" if success else "✗ FAIL"
        except Exception as e:
            print(f"✗ 错误: {e}")
            results[name] = f"✗ ERROR: {str(e)[:50]}"

    # 打印总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)

    for name, result in results.items():
        print(f"{name:20s} {result}")

    # 统计结果
    passed = sum(1 for r in results.values() if "PASS" in r)
    total = len(results)

    print("\n" + "="*70)
    print(f"测试完成: {passed}/{total} 通过")
    print("="*70)

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
