"""PubMed API 测试"""

import time
import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行PubMed API测试

    Args:
        test_config: 测试配置字典，可包含:
            - authors: 要测试的作者列表
            - max_results: 每个作者最多获取多少出版物
    """
    print_header("测试 PubMed API")

    from fetchers.pubmed import PubMedFetcher
    fetcher = PubMedFetcher()

    # 默认配置
    config = {
        "authors": ['Fauci AS', 'Collins FS'],
        "max_results": 2000  # 完整枚举
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    print("  注意: PubMed有速率限制（3 req/sec），测试可能较慢...")

    for author in config["authors"]:
        print(f"\n测试作者: {author}")
        pubs, api_info, question = fetcher.fetch_author_publications(
            author,
            max_results=config["max_results"]
        )

        result = create_test_result(
            identifier=author,
            question=question,
            api_info=api_info,
            data=pubs,
            data_key="publications",
            author=author
        )
        results.append(result)

        print(f"  ✓ 找到 {len(pubs)} 篇论文")
        if len(pubs) > 0:
            print(f"  前3篇: {pubs[:3]}")

        # 尊重速率限制
        time.sleep(1)

    save_result("pubmed", {
        "api_name": "PubMed",
        "requires_auth": False,
        "note": "速率限制: 3 req/sec",
        "config": config,
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
