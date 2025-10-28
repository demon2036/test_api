#!/usr/bin/env python3
"""测试 Docker Hub 的高级功能"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "enumerate_framework"))

from fetchers.docker import DockerFetcher


def test_docker_advanced_features():
    """测试 Docker Hub 的高级过滤功能"""
    print("=" * 60)
    print("测试 Docker Hub 高级功能")
    print("=" * 60)

    fetcher = DockerFetcher()

    # 1. 测试 fetch_with_metadata
    print("\n[测试 1] 获取 Python 镜像的元数据...")
    tags, api_info, question = fetcher.fetch_with_metadata(image='python', limit=50)
    print(f"✓ 获取了 {len(tags)} 个标签（含元数据）")

    if len(tags) > 0:
        print(f"✓ 示例标签元数据:")
        example = tags[0]
        print(f"  - 名称: {example['name']}")
        print(f"  - 最后推送: {example['last_pushed'][:19] if example['last_pushed'] else 'N/A'}")
        print(f"  - 大小: {example['size'] / 1024 / 1024:.1f} MB")
        print(f"  - 架构: {', '.join(example['architectures'])}")
        print(f"  - 操作系统: {', '.join(example['os_list'])}")

    # 2. 测试 filter_by_name_pattern (查找 alpine 标签)
    print("\n[测试 2] 过滤包含 'alpine' 的标签...")
    alpine_tags = fetcher.filter_by_name_pattern(tags, "alpine")
    print(f"✓ 找到 {len(alpine_tags)} 个 alpine 标签")
    if len(alpine_tags) > 0:
        print(f"  前5个: {[t['name'] for t in alpine_tags[:5]]}")

    # 3. 测试 filter_by_name_pattern (查找 slim 标签)
    print("\n[测试 3] 过滤包含 'slim' 的标签...")
    slim_tags = fetcher.filter_by_name_pattern(tags, "slim")
    print(f"✓ 找到 {len(slim_tags)} 个 slim 标签")
    if len(slim_tags) > 0:
        print(f"  前5个: {[t['name'] for t in slim_tags[:5]]}")

    # 4. 测试 filter_by_architecture (查找 arm64 标签)
    print("\n[测试 4] 过滤支持 arm64 架构的标签...")
    arm_tags = fetcher.filter_by_architecture(tags, "arm64")
    print(f"✓ 找到 {len(arm_tags)} 个支持 arm64 的标签")
    if len(arm_tags) > 0:
        print(f"  前5个: {[t['name'] for t in arm_tags[:5]]}")

    # 5. 测试 filter_by_architecture (查找 amd64 标签)
    print("\n[测试 5] 过滤支持 amd64 架构的标签...")
    amd_tags = fetcher.filter_by_architecture(tags, "amd64")
    print(f"✓ 找到 {len(amd_tags)} 个支持 amd64 的标签")

    # 6. 测试 sort_by_push_time (最新的)
    print("\n[测试 6] 按推送时间排序（最新的在前）...")
    sorted_tags = fetcher.sort_by_push_time(tags, reverse=True)
    print(f"✓ 排序完成，最新的5个标签:")
    for i, tag in enumerate(sorted_tags[:5], 1):
        push_time = tag['last_pushed'][:19] if tag['last_pushed'] else 'N/A'
        print(f"  {i}. {tag['name']:30s} - {push_time}")

    # 7. 测试 sort_by_push_time (最旧的)
    print("\n[测试 7] 按推送时间排序（最旧的在前）...")
    sorted_tags_old = fetcher.sort_by_push_time(tags, reverse=False)
    print(f"✓ 排序完成，最旧的5个标签:")
    for i, tag in enumerate(sorted_tags_old[:5], 1):
        push_time = tag['last_pushed'][:19] if tag['last_pushed'] else 'N/A'
        print(f"  {i}. {tag['name']:30s} - {push_time}")

    # 8. 组合过滤：alpine + arm64
    print("\n[测试 8] 组合过滤：alpine 标签 + arm64 架构...")
    alpine_arm = fetcher.filter_by_architecture(alpine_tags, "arm64")
    print(f"✓ 找到 {len(alpine_arm)} 个 alpine + arm64 标签")
    if len(alpine_arm) > 0:
        print(f"  示例: {[t['name'] for t in alpine_arm[:3]]}")

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！Docker Hub 高级功能正常工作")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_docker_advanced_features()
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
