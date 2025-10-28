"""CRAN (R Packages) API 测试"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行CRAN API测试

    Args:
        test_config: 测试配置字典，可包含:
            - packages: 要测试的R包列表
    """
    print_header("测试 CRAN (R Packages) API")

    from fetchers.cran import CRANFetcher
    fetcher = CRANFetcher()

    # 默认配置 - 流行的R包
    config = {
        "packages": ['ggplot2', 'dplyr', 'tidyr', 'shiny', 'knitr']
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    for pkg in config["packages"]:
        print(f"\n测试包: {pkg}")
        versions, api_info, question = fetcher.fetch(package=pkg)

        result = create_test_result(
            identifier=pkg,
            question=question,
            api_info=api_info,
            data=versions,
            data_key="versions",
            package=pkg
        )
        results.append(result)

        print(f"  ✓ 找到 {len(versions)} 个版本")
        print(f"  前5个版本: {versions[:5]}")
        if len(versions) > 5:
            print(f"  最新版本: {versions[-1]}")

    save_result("cran", {
        "api_name": "CRAN (R Packages)",
        "requires_auth": False,
        "config": config,
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
