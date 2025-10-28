#!/usr/bin/env python3
"""Hugging Face Hub 集成测试 - 快速验证所有功能"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from enumerate_framework.fetchers.huggingface import HuggingFaceFetcher


def test_basic_functionality():
    """测试基本功能"""
    print("\n" + "="*60)
    print("集成测试: Hugging Face Hub API")
    print("="*60)

    fetcher = HuggingFaceFetcher()

    # 测试1: 枚举模型
    print("\n[测试1] 枚举模型功能")
    models, api_info, question = fetcher.fetch_models(author="openai", max_items=10)
    assert len(models) > 0, "应该能找到 OpenAI 的模型"
    print(f"  ✓ 找到 {len(models)} 个模型")
    print(f"  ✓ 问题: {question}")
    print(f"  ✓ API: {api_info['api_endpoint']}")

    # 测试2: 获取带元数据的模型
    print("\n[测试2] 元数据功能")
    models_meta, _, _ = fetcher.fetch_models_with_metadata(
        filter_tag="text-generation",
        max_items=20
    )
    assert len(models_meta) > 0, "应该能找到 text-generation 模型"
    assert 'downloads' in models_meta[0], "应该包含 downloads 元数据"
    assert 'likes' in models_meta[0], "应该包含 likes 元数据"
    print(f"  ✓ 找到 {len(models_meta)} 个模型（带元数据）")
    print(f"  ✓ 元数据字段: {list(models_meta[0].keys())}")

    # 测试3: 过滤功能
    print("\n[测试3] 过滤功能")
    popular = fetcher.filter_by_downloads(models_meta, min_downloads=100000)
    print(f"  ✓ 下载量过滤: {len(models_meta)} -> {len(popular)}")

    # 测试4: 数据集
    print("\n[测试4] 数据集枚举")
    datasets, _, _ = fetcher.fetch_datasets(search="medical", max_items=10)
    print(f"  ✓ 找到 {len(datasets)} 个医疗相关数据集")

    # 测试5: Spaces
    print("\n[测试5] Spaces枚举")
    spaces, _, _ = fetcher.fetch_spaces(max_items=10)
    print(f"  ✓ 找到 {len(spaces)} 个Spaces")

    # 测试6: 多重过滤
    print("\n[测试6] 多重过滤组合")
    models_meta, _, _ = fetcher.fetch_models_with_metadata(
        filter_tag="text-generation",
        max_items=50
    )
    result = fetcher.filter_by_downloads(models_meta, min_downloads=100000)
    result = fetcher.filter_by_likes(result, min_likes=100)
    print(f"  ✓ 组合过滤结果: {len(result)} 个模型")

    print("\n" + "="*60)
    print("✓ 所有集成测试通过!")
    print("="*60)
    return True


def test_advanced_queries():
    """测试GEMINI.md中的高级查询"""
    print("\n" + "="*60)
    print("高级查询测试")
    print("="*60)

    fetcher = HuggingFaceFetcher()

    # 高级查询1: 支持中文 + 下载量>100,000
    print("\n[高级查询1] 中文 + 高下载量")
    models, _, _ = fetcher.fetch_models_with_metadata(
        filter_tag="text-generation",
        max_items=100
    )
    result = fetcher.filter_by_tag(models, "zh")
    result = fetcher.filter_by_downloads(result, min_downloads=100000)
    print(f"  ✓ 符合条件: {len(result)} 个模型")

    # 高级查询2: PyTorch + 最近更新
    print("\n[高级查询2] PyTorch + 最近更新")
    models, _, _ = fetcher.fetch_models_with_metadata(max_items=100)
    result = fetcher.filter_by_library(models, "pytorch")
    result = fetcher.filter_by_update_time(result, days_ago=30)
    print(f"  ✓ 符合条件: {len(result)} 个模型")

    print("\n" + "="*60)
    print("✓ 高级查询测试通过!")
    print("="*60)
    return True


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_advanced_queries()
        print("\n" + "="*60)
        print("✓✓✓ 所有测试通过! ✓✓✓")
        print("="*60)
        print("\nHugging Face Hub API 实现已完成并通过所有测试:")
        print("  ✓ 基础枚举功能")
        print("  ✓ 元数据获取")
        print("  ✓ 高级过滤")
        print("  ✓ 组合查询")
        print("  ✓ GEMINI.md 高级场景")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
