"""Hugging Face Hub API 完整测试 - 基础查询和高级过滤"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from ..utils import save_result, create_test_result, print_header


def run_basic(test_config=None):
    """运行Hugging Face API基础测试 - 枚举作者的所有资源

    Args:
        test_config: 测试配置字典，可包含:
            - models_authors: 模型作者列表
            - datasets_authors: 数据集作者列表
            - spaces_authors: Spaces作者列表
            - max_items: 每个查询最大项目数
            - api_token: Hugging Face API Token (可选)

    Returns:
        list: 测试结果列表
    """
    print_header("测试 Hugging Face Hub API - 基础查询")

    from fetchers.ai_ml.huggingface import HuggingFaceFetcher
    import os

    # 默认配置
    config = {
        "models_authors": [
            "openai-community",
            "meta-llama",
            "google"
        ],
        "datasets_authors": [
            "squad",
            "glue"
        ],
        "spaces_authors": [
            "gradio"
        ],
        "max_items": 100,
        "api_token": None
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    # 从环境变量获取API token（如果有）
    api_token = config.get('api_token') or os.getenv('HUGGINGFACE_TOKEN')

    fetcher = HuggingFaceFetcher(api_token=api_token)
    results = []

    # 测试模型查询
    print("\n[1] 测试模型查询")
    for author in config["models_authors"]:
        print(f"\n  测试作者: {author}")

        models, api_info, question = fetcher.fetch_models(
            author=author,
            max_items=config["max_items"]
        )

        result = create_test_result(
            identifier=f"models_{author}",
            question=question,
            api_info=api_info,
            data=models,
            data_key="models",
            author=author,
            resource_type="models"
        )
        results.append(result)

        print(f"  ✓ 找到 {len(models)} 个模型")
        if models:
            print(f"  前3个:")
            for model in models[:3]:
                print(f"    - {model}")

    # 测试数据集查询
    print("\n[2] 测试数据集查询")
    for author in config["datasets_authors"]:
        print(f"\n  测试作者: {author}")

        datasets, api_info, question = fetcher.fetch_datasets(
            author=author,
            max_items=config["max_items"]
        )

        result = create_test_result(
            identifier=f"datasets_{author}",
            question=question,
            api_info=api_info,
            data=datasets,
            data_key="datasets",
            author=author,
            resource_type="datasets"
        )
        results.append(result)

        print(f"  ✓ 找到 {len(datasets)} 个数据集")
        if datasets:
            print(f"  前3个:")
            for dataset in datasets[:3]:
                print(f"    - {dataset}")

    # 测试Spaces查询
    print("\n[3] 测试Spaces查询")
    for author in config["spaces_authors"]:
        print(f"\n  测试作者: {author}")

        spaces, api_info, question = fetcher.fetch_spaces(
            author=author,
            max_items=config["max_items"]
        )

        result = create_test_result(
            identifier=f"spaces_{author}",
            question=question,
            api_info=api_info,
            data=spaces,
            data_key="spaces",
            author=author,
            resource_type="spaces"
        )
        results.append(result)

        print(f"  ✓ 找到 {len(spaces)} 个Spaces")
        if spaces:
            print(f"  前3个:")
            for space in spaces[:3]:
                print(f"    - {space}")

    # 保存到 ai_ml 子文件夹
    save_result("ai_ml/huggingface", {
        "api_name": "Hugging Face Hub - Basic Tests",
        "requires_auth": False,
        "description": "枚举指定作者的所有models、datasets和spaces",
        "config": config,
        "tests": results
    })

    print("\n" + "="*80)
    print("✓ Hugging Face Hub 基础测试完成!")
    print("="*80)

    return results


def run_enhanced(test_config=None):
    """运行Hugging Face Hub增强测试 - Top N查询和元数据过滤

    测试"Top N"查询模式（符合Enumerate All原则）：
    1. 下载量最高的100个text-generation模型
    2. 点赞数最高的100个PyTorch模型
    3. 下载量最高的100个中文模型
    4. 最近更新的100个模型
    5. 下载量最高的50个医疗相关数据集
    6. 下载量最高的50个text-generation + PyTorch模型

    所有测试均使用API的sort参数进行排序，返回完整且精确的Top N结果。

    Returns:
        list: 测试结果列表
    """
    print_header("测试 Hugging Face Hub API - 高级过滤功能")

    from fetchers.ai_ml.huggingface import HuggingFaceFetcher
    import os

    # 从环境变量获取API token（如果有）
    api_token = os.getenv('HUGGINGFACE_TOKEN')
    fetcher = HuggingFaceFetcher(api_token=api_token)

    results = []

    # 测试1: 获取下载量最高的text-generation模型（Top 100）
    print("\n[测试1] 获取下载量最高的100个text-generation模型")
    print("-" * 60)

    models, api_info, question = fetcher.fetch_models_with_metadata(
        filter_tag="text-generation",
        max_items=100,
        sort="downloads",
        direction=-1  # 降序
    )

    print(f"  ✓ 获取到 {len(models)} 个text-generation模型（按下载量降序排列）")

    if models:
        print(f"  前5个热门模型:")
        for model in models[:5]:
            print(f"    - {model['id']}: {model.get('downloads', 0):,} downloads, {model.get('likes', 0)} likes")

    # 构建包含元数据的答案结构
    answer_with_metadata = [{
        'id': m['id'],
        'downloads': m.get('downloads', 0),
        'likes': m.get('likes', 0),
        'rank': idx + 1  # 排名（从1开始）
    } for idx, m in enumerate(models)]

    results.append(create_test_result(
        identifier="text_generation_top_downloads",
        question="列出下载量最高的100个text-generation模型",
        api_info=api_info,
        data=answer_with_metadata,
        data_key="models",
        filter="task=text-generation, sort=downloads(desc), limit=100"
    ))

    # 测试2: 获取点赞数最高的PyTorch模型（Top 100）
    print("\n[测试2] 获取点赞数最高的100个PyTorch模型")
    print("-" * 60)

    pytorch_models, api_info, question = fetcher.fetch_models_with_metadata(
        filter_tag="pytorch",
        max_items=100,
        sort="likes",
        direction=-1  # 降序
    )

    print(f"  ✓ 获取到 {len(pytorch_models)} 个PyTorch模型（按点赞数降序排列）")

    if pytorch_models:
        print(f"  前5个最受欢迎的模型:")
        for model in pytorch_models[:5]:
            print(f"    - {model['id']}: {model.get('likes', 0)} likes, {model.get('downloads', 0):,} downloads")

    # 构建包含元数据的答案结构
    answer_with_metadata = [{
        'id': m['id'],
        'likes': m.get('likes', 0),
        'downloads': m.get('downloads', 0),
        'rank': idx + 1
    } for idx, m in enumerate(pytorch_models)]

    results.append(create_test_result(
        identifier="pytorch_top_likes",
        question="列出点赞数最高的100个PyTorch模型",
        api_info=api_info,
        data=answer_with_metadata,
        data_key="models",
        filter="library=pytorch, sort=likes(desc), limit=100"
    ))

    # 测试3: 获取下载量最高的中文模型（Top 100）
    print("\n[测试3] 获取下载量最高的100个支持中文的模型")
    print("-" * 60)

    chinese_models, api_info, question = fetcher.fetch_models_with_metadata(
        filter_tag="zh",  # 使用中文标签过滤
        max_items=100,
        sort="downloads",
        direction=-1  # 降序
    )

    print(f"  ✓ 获取到 {len(chinese_models)} 个中文模型（按下载量降序排列）")

    if chinese_models:
        print(f"  前5个中文模型:")
        for model in chinese_models[:5]:
            print(f"    - {model['id']}: {model.get('downloads', 0):,} downloads, {model.get('pipeline_tag', 'N/A')}")

    # 构建包含元数据的答案结构
    answer_with_metadata = [{
        'id': m['id'],
        'downloads': m.get('downloads', 0),
        'pipeline_tag': m.get('pipeline_tag', 'N/A'),
        'rank': idx + 1
    } for idx, m in enumerate(chinese_models)]

    results.append(create_test_result(
        identifier="chinese_top_downloads",
        question="列出下载量最高的100个支持中文的模型",
        api_info=api_info,
        data=answer_with_metadata,
        data_key="models",
        filter="tag=zh, sort=downloads(desc), limit=100"
    ))

    # 测试4: 获取最近更新的模型（Top 100）
    print("\n[测试4] 获取最近更新的100个模型")
    print("-" * 60)

    recent_models, api_info, question = fetcher.fetch_models_with_metadata(
        max_items=100,
        sort="lastModified",  # 按最后修改时间排序
        direction=-1  # 降序（最新的在前）
    )

    print(f"  ✓ 获取到 {len(recent_models)} 个模型（按更新时间降序排列）")

    if recent_models:
        print(f"  前5个最新更新的模型:")
        for model in recent_models[:5]:
            print(f"    - {model['id']}: {model.get('last_modified', 'N/A')}")

    # 构建包含元数据的答案结构
    answer_with_metadata = [{
        'id': m['id'],
        'last_modified': m.get('last_modified', 'N/A'),
        'downloads': m.get('downloads', 0),
        'rank': idx + 1
    } for idx, m in enumerate(recent_models)]

    results.append(create_test_result(
        identifier="recently_updated_top",
        question="列出最近更新的100个模型",
        api_info=api_info,
        data=answer_with_metadata,
        data_key="models",
        filter="sort=lastModified(desc), limit=100"
    ))

    # 测试5: 获取下载量最高的医疗相关数据集（Top 50）
    print("\n[测试5] 获取下载量最高的50个医疗相关数据集")
    print("-" * 60)

    datasets, api_info, question = fetcher.fetch_datasets_with_metadata(
        search="medical",
        max_items=50,
        sort="downloads",
        direction=-1  # 降序
    )

    print(f"  ✓ 获取到 {len(datasets)} 个医疗相关数据集（按下载量降序排列）")

    if datasets:
        print(f"  前5个数据集:")
        for dataset in datasets[:5]:
            print(f"    - {dataset['id']}: {dataset.get('downloads', 0):,} downloads")

    # 构建包含元数据的答案结构
    answer_with_metadata = [{
        'id': d['id'],
        'downloads': d.get('downloads', 0),
        'likes': d.get('likes', 0),
        'rank': idx + 1
    } for idx, d in enumerate(datasets)]

    results.append(create_test_result(
        identifier="medical_top_datasets",
        question="列出下载量最高的50个医疗相关数据集",
        api_info=api_info,
        data=answer_with_metadata,
        data_key="datasets",
        filter="search='medical', sort=downloads(desc), limit=50"
    ))

    # 测试6: 组合过滤 - 下载量最高的text-generation PyTorch模型（Top 50）
    print("\n[测试6] 获取下载量最高的50个text-generation + PyTorch模型")
    print("-" * 60)

    # 先获取text-generation模型，按下载量排序
    models, api_info, question = fetcher.fetch_models_with_metadata(
        filter_tag="text-generation",
        max_items=200,  # 获取更多以便过滤
        sort="downloads",
        direction=-1
    )

    # 在客户端过滤PyTorch模型（因为API不支持同时过滤多个标签）
    pytorch_models = fetcher.filter_by_library(models, "pytorch")

    # 取前50个
    top_pytorch_models = pytorch_models[:50]

    print(f"  ✓ 获取到 {len(models)} 个text-generation模型")
    print(f"  ✓ 其中PyTorch模型: {len(pytorch_models)} 个")
    print(f"  ✓ Top 50: {len(top_pytorch_models)} 个")

    if top_pytorch_models:
        print(f"  前5个模型:")
        for model in top_pytorch_models[:5]:
            print(f"    - {model['id']}")
            print(f"      Downloads: {model.get('downloads', 0):,}")
            print(f"      Likes: {model.get('likes', 0)}")
            print(f"      Library: {model.get('library_name', 'N/A')}")

    # 构建包含元数据的答案结构
    answer_with_metadata = [{
        'id': m['id'],
        'downloads': m.get('downloads', 0),
        'likes': m.get('likes', 0),
        'library_name': m.get('library_name', 'N/A'),
        'rank': idx + 1
    } for idx, m in enumerate(top_pytorch_models)]

    results.append(create_test_result(
        identifier="text_generation_pytorch_top",
        question="列出下载量最高的50个text-generation + PyTorch模型",
        api_info=api_info,
        data=answer_with_metadata,
        data_key="models",
        filter="task=text-generation AND library=pytorch, sort=downloads(desc), limit=50"
    ))

    # 保存到 ai_ml 子文件夹
    save_result("ai_ml/huggingface_enhanced", {
        "api_name": "Hugging Face Hub - Enhanced Tests",
        "requires_auth": False,
        "description": "测试Top N查询模式：使用API排序功能获取下载量、点赞数、更新时间等维度的Top N结果",
        "tests": results
    })

    print("\n" + "="*80)
    print("✓ Hugging Face Hub 增强测试完成!")
    print("="*80)

    return results


def run(test_config=None):
    """运行所有Hugging Face Hub测试

    Args:
        test_config: 测试配置字典

    Returns:
        tuple: (basic_results, enhanced_results)
    """
    basic_results = run_basic(test_config)
    enhanced_results = run_enhanced(test_config)

    return basic_results, enhanced_results


if __name__ == "__main__":
    run()
