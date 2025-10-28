#!/usr/bin/env python3
"""统计报告生成"""

import json
from collections import defaultdict


def generate_stats(filepath: str = "output/test_cases.json"):
    """生成统计报告"""

    with open(filepath, "r") as f:
        test_cases = json.load(f)

    print("=" * 80)
    print("统计报告")
    print("=" * 80)

    # 总体统计
    total = len(test_cases)
    total_items = sum(tc['enumerate_question']['count'] for tc in test_cases)
    total_sparse = sum(len(tc['sparse_questions']) for tc in test_cases)

    print(f"\n总体:")
    print(f"  测试域: {total}")
    print(f"  项目数: {total_items:,}")
    print(f"  稀疏问题: {total_sparse}")
    print(f"  平均每域: {total_items/total:.1f} 项")

    # 按生态系统分类
    ecosystems = defaultdict(list)
    for tc in test_cases:
        eco = tc['metadata'].get('ecosystem', tc['metadata'].get('platform', 'Other'))
        ecosystems[eco].append(tc)

    print(f"\n按生态系统 ({len(ecosystems)} 个):")
    for eco, tcs in sorted(ecosystems.items(), key=lambda x: -len(x[1])):
        count = sum(tc['enumerate_question']['count'] for tc in tcs)
        print(f"  {eco:25} {len(tcs):2} 域  {count:>6,} 项")

    # Top 10
    print(f"\nTop 10 最大数据集:")
    sorted_tc = sorted(test_cases, key=lambda x: x['enumerate_question']['count'], reverse=True)
    for i, tc in enumerate(sorted_tc[:10], 1):
        count = tc['enumerate_question']['count']
        print(f"  {i:2}. {tc['domain']:30} {count:>6,} 项")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    generate_stats()
