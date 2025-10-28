"""Hugging Face Hub API 测试"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行Hugging Face API测试

    Args:
        test_config: 测试配置字典，可包含:
            - models_authors: 模型作者列表
            - datasets_authors: 数据集作者列表
            - spaces_authors: Spaces作者列表
            - max_items: 每个查询最大项目数
            - api_token: Hugging Face API Token (可选)
    """
    print_header("测试 Hugging Face Hub API")

    from fetchers.huggingface import HuggingFaceFetcher

    # 默认配置
    config = {
        "models_authors": [
            "openai",
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
        "api_token": None  # 可选：在.env中设置HUGGINGFACE_TOKEN
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    # 从环境变量获取API token（如果有）
    import os
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

    save_result("huggingface", {
        "api_name": "Hugging Face Hub",
        "requires_auth": False,
        "config": config,
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
