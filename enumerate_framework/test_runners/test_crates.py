"""Crates.io API 测试"""

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
    """运行Crates.io API测试

    Args:
        test_config: 测试配置字典，可包含:
            - crates: 要测试的crate列表
    """
    print_header("测试 Crates.io API")

    from fetchers.crates import CratesFetcher
    fetcher = CratesFetcher()

    # 默认配置
    config = {
        "crates": ['serde', 'tokio', 'regex', 'clap', 'reqwest']
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    for crate in config["crates"]:
        print(f"\n测试crate: {crate}")
        versions, api_info, question = fetcher.fetch(crate=crate)

        result = create_test_result(
            identifier=crate,
            question=question,
            api_info=api_info,
            data=versions,
            data_key="versions",
            crate=crate
        )
        results.append(result)

        print(f"  ✓ 找到 {len(versions)} 个版本")
        # 尊重速率限制
        time.sleep(1)

    save_result("crates", {
        "api_name": "Crates.io",
        "requires_auth": False,
        "config": config,
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
