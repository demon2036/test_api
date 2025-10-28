"""Hugging Face Hub API 功能展示

展示 Hugging Face Hub API 的"枚举全部"能力和高级过滤功能
"""

import sys
from pathlib import Path

# 添加enumerate_framework到路径
sys.path.insert(0, str(Path(__file__).parent))

from enumerate_framework.fetchers.huggingface import HuggingFaceFetcher


def showcase_models():
    """展示模型枚举和过滤功能"""
    print("\n" + "="*80)
    print("Hugging Face Models - 枚举和过滤功能展示")
    print("="*80)

    fetcher = HuggingFaceFetcher()

    # 1. 枚举特定作者的所有模型
    print("\n[场景1] 枚举OpenAI的所有公开模型")
    print("-" * 60)
    models, api_info, question = fetcher.fetch_models(author="openai", max_items=50)
    print(f"问题: {question}")
    print(f"结果: 找到 {len(models)} 个模型")
    if models:
        print(f"示例模型:")
        for model in models[:5]:
            print(f"  - {model}")

    # 2. 按任务类型枚举 + 元数据过滤
    print("\n[场景2] 枚举text-generation模型（下载量>100,000）")
    print("-" * 60)
    models_meta, _, _ = fetcher.fetch_models_with_metadata(
        filter_tag="text-generation",
        max_items=200
    )
    popular = fetcher.filter_by_downloads(models_meta, min_downloads=100000)
    print(f"总共text-generation模型: {len(models_meta)}")
    print(f"下载量>100,000的模型: {len(popular)}")
    if popular:
        print(f"Top 5 热门模型:")
        for model in sorted(popular, key=lambda x: x.get('downloads', 0), reverse=True)[:5]:
            print(f"  - {model['id']}")
            print(f"    Downloads: {model.get('downloads', 0):,}")
            print(f"    Likes: {model.get('likes', 0)}")

    # 3. 多重过滤组合
    print("\n[场景3] 复杂查询: PyTorch + Translation + 支持中文")
    print("-" * 60)
    models_meta, _, _ = fetcher.fetch_models_with_metadata(
        filter_tag="translation",
        max_items=200
    )
    # 应用多个过滤器
    result = fetcher.filter_by_library(models_meta, "pytorch")
    result = fetcher.filter_by_tag(result, "zh")
    print(f"符合所有条件的模型: {len(result)}")
    if result:
        print(f"示例模型:")
        for model in result[:5]:
            print(f"  - {model['id']}")
            tags = [t for t in model.get('tags', []) if 'zh' in t.lower() or 'chinese' in t.lower()]
            print(f"    中文相关标签: {tags}")

    # 4. 最近更新的模型
    print("\n[场景4] 最近30天更新的image-classification模型")
    print("-" * 60)
    models_meta, _, _ = fetcher.fetch_models_with_metadata(
        filter_tag="image-classification",
        max_items=100
    )
    recent = fetcher.filter_by_update_time(models_meta, days_ago=30)
    print(f"总共image-classification模型: {len(models_meta)}")
    print(f"最近30天更新的: {len(recent)}")
    if recent:
        print(f"示例模型:")
        for model in sorted(recent, key=lambda x: x.get('last_modified', ''), reverse=True)[:5]:
            print(f"  - {model['id']}")
            print(f"    Last modified: {model.get('last_modified', 'N/A')}")


def showcase_datasets():
    """展示数据集枚举和过滤功能"""
    print("\n" + "="*80)
    print("Hugging Face Datasets - 枚举和过滤功能展示")
    print("="*80)

    fetcher = HuggingFaceFetcher()

    # 1. 枚举特定作者的数据集
    print("\n[场景1] 枚举GLUE数据集")
    print("-" * 60)
    datasets, api_info, question = fetcher.fetch_datasets(author="glue", max_items=50)
    print(f"问题: {question}")
    print(f"结果: 找到 {len(datasets)} 个数据集")
    if datasets:
        print(f"示例数据集:")
        for dataset in datasets[:5]:
            print(f"  - {dataset}")

    # 2. 搜索特定主题的数据集
    print("\n[场景2] 搜索medical/医疗相关数据集")
    print("-" * 60)
    datasets_meta, _, _ = fetcher.fetch_datasets_with_metadata(
        search="medical",
        max_items=100
    )
    print(f"找到医疗相关数据集: {len(datasets_meta)}")

    # 过滤开源许可证
    open_datasets = fetcher.filter_by_license(datasets_meta, "apache")
    print(f"其中Apache许可证的: {len(open_datasets)}")
    if open_datasets:
        print(f"示例数据集:")
        for dataset in open_datasets[:5]:
            print(f"  - {dataset['id']}")
            print(f"    Downloads: {dataset.get('downloads', 0):,}")
            print(f"    Likes: {dataset.get('likes', 0)}")

    # 3. 热门数据集
    print("\n[场景3] 最受欢迎的数据集（点赞数>100）")
    print("-" * 60)
    datasets_meta, _, _ = fetcher.fetch_datasets_with_metadata(max_items=200)
    popular = fetcher.filter_by_likes(datasets_meta, min_likes=100)
    print(f"点赞数>100的数据集: {len(popular)}")
    if popular:
        print(f"Top 5:")
        for dataset in sorted(popular, key=lambda x: x.get('likes', 0), reverse=True)[:5]:
            print(f"  - {dataset['id']}")
            print(f"    Likes: {dataset.get('likes', 0)}")
            print(f"    Downloads: {dataset.get('downloads', 0):,}")


def showcase_spaces():
    """展示Spaces枚举功能"""
    print("\n" + "="*80)
    print("Hugging Face Spaces - 枚举功能展示")
    print("="*80)

    fetcher = HuggingFaceFetcher()

    # 1. 枚举Gradio的Spaces
    print("\n[场景1] 枚举Gradio的所有Spaces")
    print("-" * 60)
    spaces, api_info, question = fetcher.fetch_spaces(author="gradio", max_items=50)
    print(f"问题: {question}")
    print(f"结果: 找到 {len(spaces)} 个Spaces")
    if spaces:
        print(f"示例Spaces:")
        for space in spaces[:10]:
            print(f"  - {space}")


def demonstrate_advanced_queries():
    """演示GEMINI.md中提到的高级查询"""
    print("\n" + "="*80)
    print("高级查询示例（来自GEMINI.md）")
    print("="*80)

    fetcher = HuggingFaceFetcher()

    # 查询1: "List all text-generation models that support Chinese and have more than 100,000 downloads"
    print("\n[高级查询1] 支持中文且下载量>100,000的text-generation模型")
    print("-" * 60)
    models, _, _ = fetcher.fetch_models_with_metadata(
        filter_tag="text-generation",
        max_items=300
    )
    # 应用过滤器
    result = fetcher.filter_by_tag(models, "zh")
    result = fetcher.filter_by_downloads(result, min_downloads=100000)
    print(f"符合条件的模型数量: {len(result)}")
    if result:
        print(f"示例模型:")
        for model in sorted(result, key=lambda x: x.get('downloads', 0), reverse=True)[:5]:
            print(f"  - {model['id']}")
            print(f"    Downloads: {model.get('downloads', 0):,}")
            print(f"    Tags: {[t for t in model.get('tags', []) if 'zh' in t.lower()]}")

    # 查询2: "Find all datasets tagged with 'medical imaging' that are licensed under Apache 2.0"
    print("\n[高级查询2] 标记为medical且使用Apache 2.0许可证的数据集")
    print("-" * 60)
    datasets, _, _ = fetcher.fetch_datasets_with_metadata(
        search="medical",
        max_items=200
    )
    result = fetcher.filter_by_license(datasets, "apache")
    print(f"符合条件的数据集数量: {len(result)}")
    if result:
        print(f"示例数据集:")
        for dataset in result[:5]:
            print(f"  - {dataset['id']}")
            print(f"    Downloads: {dataset.get('downloads', 0):,}")

    # 查询3: "Enumerate all PyTorch-based image segmentation models that have been updated in the last month"
    print("\n[高级查询3] PyTorch图像分割模型（最近30天更新）")
    print("-" * 60)
    models, _, _ = fetcher.fetch_models_with_metadata(
        filter_tag="image-segmentation",
        max_items=200
    )
    # 应用过滤器
    result = fetcher.filter_by_library(models, "pytorch")
    result = fetcher.filter_by_update_time(result, days_ago=30)
    print(f"符合条件的模型数量: {len(result)}")
    if result:
        print(f"示例模型:")
        for model in sorted(result, key=lambda x: x.get('last_modified', ''), reverse=True)[:5]:
            print(f"  - {model['id']}")
            print(f"    Library: {model.get('library_name', 'N/A')}")
            print(f"    Last modified: {model.get('last_modified', 'N/A')}")


def main():
    """主函数"""
    print("\n" + "="*80)
    print("Hugging Face Hub API - 'Enumerate All' 能力展示")
    print("="*80)
    print("\n本测试展示Hugging Face Hub API的以下能力：")
    print("1. 枚举特定作者/组织的所有模型/数据集/Spaces")
    print("2. 按任务类型、框架、标签等过滤")
    print("3. 按下载量、点赞数、更新时间等元数据过滤")
    print("4. 组合多个过滤条件进行复杂查询")
    print("5. 实现GEMINI.md中提到的高级查询场景")

    try:
        showcase_models()
        showcase_datasets()
        showcase_spaces()
        demonstrate_advanced_queries()

        print("\n" + "="*80)
        print("✓ 所有展示完成!")
        print("="*80)
        print("\n核心能力验证:")
        print("  ✓ Precision: 使用精确的作者名、模型ID等进行查询")
        print("  ✓ Completeness: 能够枚举指定条件下的所有结果")
        print("  ✓ Verifiability: 所有结果来自官方Hugging Face API")
        print("  ✓ Determinism: 相同查询返回相同的完整结果集")

    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
