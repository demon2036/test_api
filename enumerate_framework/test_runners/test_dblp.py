"""DBLP API 测试

DBLP使用PID（永久标识符）系统，完全符合"列举全部"的精确性要求。
"""

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
    """运行DBLP API测试

    Args:
        test_config: 测试配置字典，可包含:
            - authors: 要测试的作者列表（格式：[{"pid": "l/YannLeCun", "name": "Yann LeCun"}, ...]）
            - max_publications: 每个作者最多获取多少出版物（默认10000）
    """
    print_header("测试 DBLP API (计算机科学文献数据库)")

    from fetchers.dblp import DBLPFetcher
    fetcher = DBLPFetcher()

    # 默认配置 - 使用知名计算机科学家的PID
    config = {
        "authors": [
            {"pid": "l/YannLeCun", "name": "Yann LeCun"},
            {"pid": "h/GeoffreyEHinton", "name": "Geoffrey E. Hinton"},
            {"pid": "b/YoshuaBengio", "name": "Yoshua Bengio"}
        ],
        "max_publications": 10000  # 完整枚举
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    print("\n说明:")
    print("  DBLP使用PID（永久标识符）而非作者名字")
    print("  PID永不改变，确保精确且完整地枚举所有出版物")
    print("  这完全符合'列举全部'的核心理念\n")

    for author_info in config["authors"]:
        pid = author_info["pid"]
        author_name = author_info.get("name", pid)

        print(f"\n测试作者: {author_name}")
        print(f"  PID: {pid}")
        print(f"  最大获取数: {config['max_publications']} (完整枚举)")

        publications, api_info, question = fetcher.fetch_by_pid(
            pid=pid,
            max_publications=config["max_publications"]
        )

        result = create_test_result(
            identifier=pid,
            question=question,
            api_info=api_info,
            data=publications,
            data_key="publications",
            pid=pid,
            author_name=author_name
        )
        results.append(result)

        print(f"  ✓ 找到 {len(publications)} 篇出版物")
        if len(publications) > 0:
            print(f"  前3篇: {publications[:3]}")

        # 轻微延迟，尊重服务器
        time.sleep(1)

    save_result("dblp", {
        "api_name": "DBLP",
        "requires_auth": False,
        "identifier_system": "PID (永久标识符)",
        "precision": "100% - 使用唯一PID，无歧义",
        "config": config,
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
