"""Open Library API 测试"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行Open Library API测试

    Args:
        test_config: 测试配置字典，可包含:
            - authors: 要测试的作者列表（格式：[{"key": "OL34221A", "name": "Isaac Asimov"}, ...]）
            - max_works: 每个作者最多获取多少作品
    """
    print_header("测试 Open Library API")

    from fetchers.goodreads import OpenLibraryFetcher
    fetcher = OpenLibraryFetcher()

    # 默认配置
    config = {
        "authors": [
            {"key": "OL34221A", "name": "Isaac Asimov"},
            {"key": "OL23919A", "name": "J.R.R. Tolkien"}
        ],
        "max_works": 200
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    for author_info in config["authors"]:
        author_key = author_info["key"]
        author_name = author_info.get("name", author_key)

        print(f"\n测试作者: {author_key} ({author_name})")
        works, api_info, question = fetcher.fetch_author_works(
            author_key,
            max_works=config["max_works"]
        )

        result = create_test_result(
            identifier=author_key,
            question=question,
            api_info=api_info,
            data=works,
            data_key="works",
            author_key=author_key,
            author_name=author_name
        )
        results.append(result)

        print(f"  ✓ 找到 {len(works)} 部作品")
        if len(works) > 0:
            print(f"  前5部: {works[:5]}")

    save_result("openlibrary", {
        "api_name": "Open Library",
        "requires_auth": False,
        "config": config,
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
