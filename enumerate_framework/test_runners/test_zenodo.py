"""Zenodo Research Repository API 测试"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行Zenodo API测试

    Args:
        test_config: 测试配置字典，可包含:
            - researchers: 研究者列表，每个包含orcid和name
            - communities: 社区ID列表
            - max_records: 每个查询最大记录数
    """
    print_header("测试 Zenodo Research Repository API")

    from fetchers.zenodo import ZenodoFetcher
    fetcher = ZenodoFetcher()

    # 默认配置 - 使用ORCID精确查询
    config = {
        "researchers": [
            {"orcid": "0000-0002-1825-0097", "name": "Rees, Joanna"},
            {"orcid": "0000-0001-6001-1296", "name": "Brown, Josh"}
        ],
        "max_records": 100
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    # 测试ORCID查询
    for researcher in config["researchers"]:
        orcid = researcher["orcid"]
        name = researcher.get("name", "Unknown")

        print(f"\n测试研究者: {name}")
        print(f"  ORCID: {orcid}")

        records, api_info, question = fetcher.fetch_by_orcid(
            orcid=orcid,
            max_records=config["max_records"]
        )

        result = create_test_result(
            identifier=orcid,
            question=question,
            api_info=api_info,
            data=records,
            data_key="records",
            orcid=orcid,
            name=name
        )
        results.append(result)

        print(f"  ✓ 找到 {len(records)} 条记录")
        if records:
            print(f"  前3条:")
            for record in records[:3]:
                print(f"    - {record}")

    save_result("zenodo", {
        "api_name": "Zenodo Research Repository",
        "requires_auth": False,
        "config": config,
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
