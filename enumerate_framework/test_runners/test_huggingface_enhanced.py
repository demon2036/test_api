"""Hugging Face Hub API 增强测试 - 测试高级过滤功能"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行Hugging Face Hub增强测试

    测试高级功能包括：
    1. 按下载量过滤模型
    2. 按点赞数过滤
    3. 按任务类型过滤
    4. 按框架过滤
    5. 按标签过滤
    6. 按更新时间过滤
    """
    print_header("测试 Hugging Face Hub API - 高级过滤功能")

    from fetchers.huggingface import HuggingFaceFetcher
    import os

    # 从环境变量获取API token（如果有）
    api_token = os.getenv('HUGGINGFACE_TOKEN')
    fetcher = HuggingFaceFetcher(api_token=api_token)

    results = []

    # 测试1: 获取text-generation模型并按下载量过滤
    print("\n[测试1] 获取text-generation模型（下载量>100,000）")
    print("-" * 60)

    models, api_info, question = fetcher.fetch_models_with_metadata(
        filter_tag="text-generation",
        max_items=200
    )

    print(f"  ✓ 获取到 {len(models)} 个text-generation模型")

    # 过滤下载量大于100,000的模型
    popular_models = fetcher.filter_by_downloads(models, min_downloads=100000)
    print(f"  ✓ 其中下载量>100,000的: {len(popular_models)} 个")

    if popular_models:
        print(f"  前5个热门模型:")
        for model in sorted(popular_models, key=lambda x: x.get('downloads', 0), reverse=True)[:5]:
            print(f"    - {model['id']}: {model.get('downloads', 0):,} downloads, {model.get('likes', 0)} likes")

    results.append(create_test_result(
        identifier="text_generation_popular",
        question="列出下载量超过100,000的text-generation模型",
        api_info=api_info,
        data=[m['id'] for m in popular_models],
        data_key="models",
        filter="downloads > 100000"
    ))

    # 测试2: 获取PyTorch模型并按点赞数过滤
    print("\n[测试2] 获取PyTorch模型（点赞数>1,000）")
    print("-" * 60)

    pytorch_models, api_info, question = fetcher.fetch_models_with_metadata(
        filter_tag="pytorch",
        max_items=200
    )

    print(f"  ✓ 获取到 {len(pytorch_models)} 个PyTorch模型")

    # 过滤点赞数大于1000的模型
    liked_models = fetcher.filter_by_likes(pytorch_models, min_likes=1000)
    print(f"  ✓ 其中点赞数>1,000的: {len(liked_models)} 个")

    if liked_models:
        print(f"  前5个最受欢迎的模型:")
        for model in sorted(liked_models, key=lambda x: x.get('likes', 0), reverse=True)[:5]:
            print(f"    - {model['id']}: {model.get('likes', 0)} likes, {model.get('downloads', 0):,} downloads")

    results.append(create_test_result(
        identifier="pytorch_liked",
        question="列出点赞数超过1,000的PyTorch模型",
        api_info=api_info,
        data=[m['id'] for m in liked_models],
        data_key="models",
        filter="likes > 1000 AND framework = pytorch"
    ))

    # 测试3: 获取中文相关模型
    print("\n[测试3] 获取支持中文的模型（包含'zh'或'chinese'标签）")
    print("-" * 60)

    all_models, api_info, question = fetcher.fetch_models_with_metadata(
        max_items=500
    )

    print(f"  ✓ 获取到 {len(all_models)} 个模型")

    # 过滤包含中文标签的模型
    chinese_models = fetcher.filter_by_tag(all_models, "zh")
    print(f"  ✓ 其中支持中文的: {len(chinese_models)} 个")

    if chinese_models:
        print(f"  前5个中文模型:")
        for model in chinese_models[:5]:
            print(f"    - {model['id']}: {model.get('pipeline_tag', 'N/A')}")

    results.append(create_test_result(
        identifier="chinese_models",
        question="列出支持中文的所有模型",
        api_info=api_info,
        data=[m['id'] for m in chinese_models],
        data_key="models",
        filter="tag contains 'zh'"
    ))

    # 测试4: 获取最近30天更新的模型
    print("\n[测试4] 获取最近30天更新的模型")
    print("-" * 60)

    recent_models = fetcher.filter_by_update_time(all_models, days_ago=30)
    print(f"  ✓ 最近30天更新的模型: {len(recent_models)} 个")

    if recent_models:
        print(f"  前5个最新更新的模型:")
        for model in sorted(recent_models, key=lambda x: x.get('last_modified', ''), reverse=True)[:5]:
            print(f"    - {model['id']}: {model.get('last_modified', 'N/A')}")

    results.append(create_test_result(
        identifier="recently_updated",
        question="列出最近30天内更新的模型",
        api_info=api_info,
        data=[m['id'] for m in recent_models],
        data_key="models",
        filter="last_modified within 30 days"
    ))

    # 测试5: 获取医疗相关数据集（Apache 2.0许可证）
    print("\n[测试5] 获取医疗相关数据集")
    print("-" * 60)

    datasets, api_info, question = fetcher.fetch_datasets_with_metadata(
        search="medical",
        max_items=100
    )

    print(f"  ✓ 获取到 {len(datasets)} 个医疗相关数据集")

    # 过滤Apache 2.0许可证
    apache_datasets = fetcher.filter_by_license(datasets, "apache")
    print(f"  ✓ 其中Apache许可证的: {len(apache_datasets)} 个")

    if apache_datasets:
        print(f"  前5个数据集:")
        for dataset in apache_datasets[:5]:
            print(f"    - {dataset['id']}: {dataset.get('downloads', 0):,} downloads")

    results.append(create_test_result(
        identifier="medical_datasets",
        question="列出医疗相关且使用Apache 2.0许可证的数据集",
        api_info=api_info,
        data=[d['id'] for d in apache_datasets],
        data_key="datasets",
        filter="search = 'medical' AND license = 'apache'"
    ))

    # 测试6: 组合过滤 - text-generation + PyTorch + 下载量>50,000
    print("\n[测试6] 组合过滤: text-generation + PyTorch + 下载量>50,000")
    print("-" * 60)

    models, api_info, question = fetcher.fetch_models_with_metadata(
        filter_tag="text-generation",
        max_items=300
    )

    # 应用多个过滤器
    filtered = fetcher.filter_by_library(models, "pytorch")
    filtered = fetcher.filter_by_downloads(filtered, min_downloads=50000)

    print(f"  ✓ 符合所有条件的模型: {len(filtered)} 个")

    if filtered:
        print(f"  前5个模型:")
        for model in sorted(filtered, key=lambda x: x.get('downloads', 0), reverse=True)[:5]:
            print(f"    - {model['id']}")
            print(f"      Downloads: {model.get('downloads', 0):,}")
            print(f"      Likes: {model.get('likes', 0)}")
            print(f"      Library: {model.get('library_name', 'N/A')}")

    results.append(create_test_result(
        identifier="combined_filter",
        question="列出text-generation任务的PyTorch模型（下载量>50,000）",
        api_info=api_info,
        data=[m['id'] for m in filtered],
        data_key="models",
        filter="task = text-generation AND library = pytorch AND downloads > 50000"
    ))

    # 保存结果
    save_result("huggingface_enhanced", {
        "api_name": "Hugging Face Hub - Enhanced Tests",
        "requires_auth": False,
        "description": "测试高级过滤功能：下载量、点赞数、任务类型、框架、标签、更新时间等",
        "tests": results
    })

    print("\n" + "="*80)
    print("✓ Hugging Face Hub 增强测试完成!")
    print("="*80)

    return results


if __name__ == "__main__":
    run()
