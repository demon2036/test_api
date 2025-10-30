"""Hugging Face Hub API 完整测试 - 基础查询和高级过滤"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from ..utils import save_result, create_test_result, print_header


# ============================================================================
# 配置常量
# ============================================================================

# 基础测试配置：定义要测试的资源类型和作者列表
BASIC_TEST_SUITE = [
    {
        "resource_type": "models",
        "authors": ["openai-community", "meta-llama", "google", "microsoft"],
        "display_name": "模型"
    },
    # {
    #     "resource_type": "datasets",
    #     "authors": ["squad", "glue"],
    #     "display_name": "数据集"
    # },
    # {
    #     "resource_type": "spaces",
    #     "authors": ["gradio"],
    #     "display_name": "Spaces"
    # }
]

# 增强测试配置：定义Top N查询的测试用例
ENHANCED_TEST_SUITE = [
    {
        "test_id": "text_generation_top_downloads",
        "question": "列出下载量最高的100个text-generation模型",
        "description": "获取下载量最高的100个text-generation模型",
        "resource_type": "models",
        "filter_tag": "text-generation",
        "sort": "downloads",
        "max_items": 100,
        "metadata_fields": ['id', 'downloads', 'likes', 'rank'],
        "filter_desc": "task=text-generation, sort=downloads(desc), limit=100"
    },
    {
        "test_id": "pytorch_top_likes",
        "question": "列出点赞数最高的100个PyTorch模型",
        "description": "获取点赞数最高的100个PyTorch模型",
        "resource_type": "models",
        "filter_tag": "pytorch",
        "sort": "likes",
        "max_items": 100,
        "metadata_fields": ['id', 'likes', 'downloads', 'rank'],
        "filter_desc": "library=pytorch, sort=likes(desc), limit=100"
    },
    {
        "test_id": "chinese_top_downloads",
        "question": "列出下载量最高的100个支持中文的模型",
        "description": "获取下载量最高的100个支持中文的模型",
        "resource_type": "models",
        "filter_tag": "zh",
        "sort": "downloads",
        "max_items": 100,
        "metadata_fields": ['id', 'downloads', 'pipeline_tag', 'rank'],
        "filter_desc": "tag=zh, sort=downloads(desc), limit=100"
    },
    {
        "test_id": "recently_updated_top",
        "question": "列出最近更新的100个模型",
        "description": "获取最近更新的100个模型",
        "resource_type": "models",
        "sort": "lastModified",
        "max_items": 100,
        "metadata_fields": ['id', 'last_modified', 'downloads', 'rank'],
        "filter_desc": "sort=lastModified(desc), limit=100"
    },
    {
        "test_id": "medical_top_datasets",
        "question": "列出下载量最高的50个医疗相关数据集",
        "description": "获取下载量最高的50个医疗相关数据集",
        "resource_type": "datasets",
        "search": "medical",
        "sort": "downloads",
        "max_items": 50,
        "metadata_fields": ['id', 'downloads', 'likes', 'rank'],
        "filter_desc": "search='medical', sort=downloads(desc), limit=50"
    },
    {
        "test_id": "text_generation_pytorch_top",
        "question": "列出下载量最高的50个text-generation + PyTorch模型",
        "description": "获取下载量最高的50个text-generation + PyTorch模型",
        "resource_type": "models",
        "filter_tag": "text-generation",
        "sort": "downloads",
        "max_items": 200,
        "secondary_filter": {"library": "pytorch"},
        "final_limit": 50,
        "metadata_fields": ['id', 'downloads', 'likes', 'library_name', 'rank'],
        "filter_desc": "task=text-generation AND library=pytorch, sort=downloads(desc), limit=50"
    },
    # === 新增：任务类型多样性 ===
    {
        "test_id": "image_classification_top_downloads",
        "question": "列出下载量最高的100个image-classification模型",
        "description": "获取下载量最高的100个image-classification模型",
        "resource_type": "models",
        "filter_tag": "image-classification",
        "sort": "downloads",
        "max_items": 100,
        "metadata_fields": ['id', 'downloads', 'likes', 'rank'],
        "filter_desc": "task=image-classification, sort=downloads(desc), limit=100"
    },
    {
        "test_id": "question_answering_top_downloads",
        "question": "列出下载量最高的100个question-answering模型",
        "description": "获取下载量最高的100个question-answering模型",
        "resource_type": "models",
        "filter_tag": "question-answering",
        "sort": "downloads",
        "max_items": 100,
        "metadata_fields": ['id', 'downloads', 'likes', 'rank'],
        "filter_desc": "task=question-answering, sort=downloads(desc), limit=100"
    },
    {
        "test_id": "text_classification_top_likes",
        "question": "列出点赞数最高的100个text-classification模型",
        "description": "获取点赞数最高的100个text-classification模型",
        "resource_type": "models",
        "filter_tag": "text-classification",
        "sort": "likes",
        "max_items": 100,
        "metadata_fields": ['id', 'likes', 'downloads', 'rank'],
        "filter_desc": "task=text-classification, sort=likes(desc), limit=100"
    },
    # === 新增：框架多样性 ===
    {
        "test_id": "tensorflow_top_likes",
        "question": "列出点赞数最高的100个TensorFlow模型",
        "description": "获取点赞数最高的100个TensorFlow模型",
        "resource_type": "models",
        "filter_tag": "tf",
        "sort": "likes",
        "max_items": 100,
        "metadata_fields": ['id', 'likes', 'downloads', 'rank'],
        "filter_desc": "library=tensorflow, sort=likes(desc), limit=100"
    },
    {
        "test_id": "jax_top_downloads",
        "question": "列出下载量最高的100个JAX模型",
        "description": "获取下载量最高的100个JAX模型",
        "resource_type": "models",
        "filter_tag": "jax",
        "sort": "downloads",
        "max_items": 100,
        "metadata_fields": ['id', 'downloads', 'likes', 'rank'],
        "filter_desc": "library=jax, sort=downloads(desc), limit=100"
    },
    # === 新增：语言多样性 ===
    {
        "test_id": "english_top_downloads",
        "question": "列出下载量最高的100个支持英文的模型",
        "description": "获取下载量最高的100个支持英文的模型",
        "resource_type": "models",
        "filter_tag": "en",
        "sort": "downloads",
        "max_items": 100,
        "metadata_fields": ['id', 'downloads', 'pipeline_tag', 'rank'],
        "filter_desc": "tag=en, sort=downloads(desc), limit=100"
    },
    {
        "test_id": "multilingual_top_likes",
        "question": "列出点赞数最高的100个多语言模型",
        "description": "获取点赞数最高的100个多语言模型",
        "resource_type": "models",
        "filter_tag": "multilingual",
        "sort": "likes",
        "max_items": 100,
        "metadata_fields": ['id', 'likes', 'downloads', 'rank'],
        "filter_desc": "tag=multilingual, sort=likes(desc), limit=100"
    },
    {
        "test_id": "japanese_top_downloads",
        "question": "列出下载量最高的100个支持日文的模型",
        "description": "获取下载量最高的100个支持日文的模型",
        "resource_type": "models",
        "filter_tag": "ja",
        "sort": "downloads",
        "max_items": 100,
        "metadata_fields": ['id', 'downloads', 'pipeline_tag', 'rank'],
        "filter_desc": "tag=ja, sort=downloads(desc), limit=100"
    },
    # === 新增：数据集领域多样性 ===
    {
        "test_id": "finance_top_datasets",
        "question": "列出下载量最高的50个金融相关数据集",
        "description": "获取下载量最高的50个金融相关数据集",
        "resource_type": "datasets",
        "search": "finance",
        "sort": "downloads",
        "max_items": 50,
        "metadata_fields": ['id', 'downloads', 'likes', 'rank'],
        "filter_desc": "search='finance', sort=downloads(desc), limit=50"
    },
    {
        "test_id": "code_top_datasets",
        "question": "列出下载量最高的50个代码相关数据集",
        "description": "获取下载量最高的50个代码相关数据集",
        "resource_type": "datasets",
        "search": "code",
        "sort": "downloads",
        "max_items": 50,
        "metadata_fields": ['id', 'downloads', 'likes', 'rank'],
        "filter_desc": "search='code', sort=downloads(desc), limit=50"
    },
    # === 新增：组合过滤多样性 ===
    {
        "test_id": "image_classification_tensorflow_top",
        "question": "列出下载量最高的50个image-classification + TensorFlow模型",
        "description": "获取下载量最高的50个image-classification + TensorFlow模型",
        "resource_type": "models",
        "filter_tag": "image-classification",
        "sort": "downloads",
        "max_items": 200,
        "secondary_filter": {"library": "tf"},
        "final_limit": 50,
        "metadata_fields": ['id', 'downloads', 'likes', 'library_name', 'rank'],
        "filter_desc": "task=image-classification AND library=tensorflow, sort=downloads(desc), limit=50"
    },
    {
        "test_id": "question_answering_multilingual_top",
        "question": "列出下载量最高的50个question-answering + 多语言模型",
        "description": "获取下载量最高的50个question-answering + 多语言模型",
        "resource_type": "models",
        "filter_tag": "question-answering",
        "sort": "downloads",
        "max_items": 200,
        "secondary_filter": {"tag": "multilingual"},
        "final_limit": 50,
        "metadata_fields": ['id', 'downloads', 'likes', 'pipeline_tag', 'rank'],
        "filter_desc": "task=question-answering AND tag=multilingual, sort=downloads(desc), limit=50"
    }
]


# ============================================================================
# 辅助函数
# ============================================================================

def _extract_metadata(items, fields):
    """通用元数据提取器

    Args:
        items: 资源列表
        fields: 需要提取的字段列表

    Returns:
        list: 包含指定字段的字典列表
    """
    result = []
    for idx, item in enumerate(items):
        entry = {}
        for field in fields:
            if field == 'rank':
                entry['rank'] = idx + 1
            elif field == 'id':
                entry['answer'] = item.get('id', 'N/A')
            else:
                # 根据字段名选择合适的默认值
                default_value = 0 if field in ['downloads', 'likes'] else 'N/A'
                entry[field] = item.get(field, default_value)

        if 'answer' not in entry:
            entry['answer'] = item.get('id', 'N/A')
        result.append(entry)
    return result


def _run_basic_resource_test(fetcher, resource_type, authors, display_name, config):
    """运行单个资源类型的基础测试

    Args:
        fetcher: HuggingFaceFetcher实例
        resource_type: 资源类型 (models/datasets/spaces)
        authors: 作者列表
        display_name: 显示名称（用于打印）
        config: 配置字典

    Returns:
        list: 测试结果列表
    """
    results = []

    # 动态获取对应的fetcher方法
    fetch_method = getattr(fetcher, f"fetch_{resource_type}")

    for author in authors:
        print(f"\n  测试作者: {author}")

        # 调用对应的fetch方法（使用 basic_max_items 以实现真正穷举）
        items, api_info, question = fetch_method(
            author=author,
            max_items=config["basic_max_items"]
        )

        # 创建测试结果
        result = create_test_result(
            question=question,
            answers=items,
            api_info=api_info,
            author=author,
            resource_type=resource_type,
            test_id=f"{resource_type}_{author}",
            query_category=fetcher.QUESTION_TYPES["basic"]
        )
        result["answer_count"] = len(items)
        results.append(result)

        # 打印结果
        print(f"  ✓ 找到 {len(items)} 个{display_name}")
        if items:
            print(f"  前3个:")
            for item in items[:3]:
                print(f"    - {item}")

    return results


def _run_enhanced_test(fetcher, test_spec):
    """运行单个增强测试

    Args:
        fetcher: HuggingFaceFetcher实例
        test_spec: 测试规范字典

    Returns:
        dict: 测试结果
    """
    print(f"\n[测试] {test_spec['description']}")
    print("-" * 60)

    resource_type = test_spec["resource_type"]

    # 选择对应的fetch方法
    if resource_type == "models":
        fetch_method = fetcher.fetch_models_with_metadata
    elif resource_type == "datasets":
        fetch_method = fetcher.fetch_datasets_with_metadata
    else:
        raise ValueError(f"不支持的资源类型: {resource_type}")

    # 构建fetch参数
    fetch_kwargs = {
        "max_items": test_spec["max_items"],
        "sort": test_spec["sort"],
        "direction": -1
    }

    if "filter_tag" in test_spec:
        fetch_kwargs["filter_tag"] = test_spec["filter_tag"]

    if "search" in test_spec:
        fetch_kwargs["search"] = test_spec["search"]

    # 调用fetch方法
    items, api_info, question = fetch_method(**fetch_kwargs)

    # 处理二次过滤（如text-generation + pytorch）
    if "secondary_filter" in test_spec:
        secondary = test_spec["secondary_filter"]

        # 根据过滤类型调用对应方法
        if "library" in secondary:
            items = fetcher.filter_by_library(items, secondary["library"])
        elif "tag" in secondary:
            items = fetcher.filter_by_tag(items, secondary["tag"])

        if "final_limit" in test_spec:
            items = items[:test_spec["final_limit"]]

    # 打印结果统计
    print(f"  ✓ 获取到 {len(items)} 个{resource_type}")

    if items:
        print(f"  前5个:")
        for item in items[:5]:
            # 动态构建显示信息
            info_parts = [f"    - {item['id']}"]

            if 'downloads' in test_spec['metadata_fields']:
                info_parts.append(f"{item.get('downloads', 0):,} downloads")
            if 'likes' in test_spec['metadata_fields']:
                info_parts.append(f"{item.get('likes', 0)} likes")
            if 'last_modified' in test_spec['metadata_fields']:
                info_parts.append(f"更新于 {item.get('last_modified', 'N/A')}")

            print(": ".join(info_parts))

    # 提取元数据
    answer_with_metadata = _extract_metadata(items, test_spec['metadata_fields'])

    # 确定展示数量（考虑二次过滤）
    intended_limit = test_spec.get("final_limit", test_spec["max_items"])

    advanced_question = fetcher.build_advanced_question(
        resource_type=resource_type,
        sort=test_spec["sort"],
        limit=intended_limit,
        direction=fetch_kwargs.get("direction", -1),
        filter_tag=test_spec.get("filter_tag"),
        search=test_spec.get("search"),
        secondary_filters=test_spec.get("secondary_filter")
    )

    # 创建测试结果
    result = create_test_result(
        question=advanced_question,
        answers=answer_with_metadata,
        api_info=api_info,
        filter=test_spec["filter_desc"],
        resource_type=resource_type,
        test_id=test_spec["test_id"],
        query_category=fetcher.QUESTION_TYPES["advanced"],
        original_question=test_spec["question"]
    )
    result["answer_count"] = len(answer_with_metadata)
    return result


def run(test_config=None):
    """运行所有Hugging Face Hub测试 - 基础查询和高级过滤

    Args:
        test_config: 测试配置字典 (可选)
            - max_items: 每个查询最大项目数
            - api_token: Hugging Face API Token

    Returns:
        list: 所有测试结果列表
    """
    print_header("测试 Hugging Face Hub API - 完整测试套件")

    from fetchers.ai_ml.huggingface import HuggingFaceFetcher
    import os

    # 配置
    # basic_max_items: 基础作者枚举测试的最大项目数（设置较大值以实现真正的穷举）
    # enhanced tests 的 max_items 在 ENHANCED_TEST_SUITE 中单独定义
    config = {"basic_max_items": 10000, "api_token": None}
    if test_config:
        config.update(test_config)

    # 从环境变量获取API token
    api_token = config.get('api_token') or os.getenv('HUGGINGFACE_TOKEN')
    fetcher = HuggingFaceFetcher(api_token=api_token)

    all_results = []

    # === 第一部分：基础测试 ===
    print("\n" + "="*80)
    print("第一部分：基础作者枚举测试")
    print("="*80)

    for idx, test_suite in enumerate(BASIC_TEST_SUITE, 1):
        print(f"\n[{idx}] 测试{test_suite['display_name']}查询")

        test_results = _run_basic_resource_test(
            fetcher=fetcher,
            resource_type=test_suite["resource_type"],
            authors=test_suite["authors"],
            display_name=test_suite["display_name"],
            config=config
        )
        all_results.extend(test_results)

    # === 第二部分：高级测试 ===
    print("\n" + "="*80)
    print("第二部分：Top N 排序和过滤测试")
    print("="*80)

    for test_spec in ENHANCED_TEST_SUITE:
        result = _run_enhanced_test(fetcher, test_spec)
        all_results.append(result)

    # === 统一保存所有结果 ===
    save_result("ai_ml/huggingface", {
        "api_name": "Hugging Face Hub API",
        "requires_auth": False,
        "description": "完整测试：基础作者枚举 + Top N排序查询 + 元数据过滤",
        "test_count": len(all_results),
        "tests": all_results
    })

    print("\n" + "="*80)
    print(f"✓ Hugging Face Hub 完整测试完成! 共 {len(all_results)} 个测试")
    print("="*80)

    return all_results


if __name__ == "__main__":
    run()
