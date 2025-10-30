"""Homebrew Formulae API 测试"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
    from test_runners.code_ecosystem.test_configs.package_config import get_config
else:
    from ..utils import save_result, create_test_result, print_header
    from .test_configs.package_config import get_config


def run(test_config=None):
    """运行Homebrew API测试

    Args:
        test_config: 测试配置字典，可包含:
            - formulae: 要测试的formula列表
    """
    print_header("测试 Homebrew Formulae API")

    from fetchers.code_ecosystem.homebrew import HomebrewFetcher
    fetcher = HomebrewFetcher()

    # 从配置文件加载
    config = get_config("homebrew")
    formulae = config["packages"]

    # 合并用户配置
    if test_config and "formulae" in test_config:
        formulae = test_config["formulae"]

    results = []

    for formula in formulae:
        print(f"\n测试formula: {formula}")
        versions, api_info, question = fetcher.fetch(formula=formula)

        answers = [
            {
                "answer": version,
                "variant_type": "stable" if idx == 0 else "versioned_formula"
            }
            for idx, version in enumerate(versions)
        ]

        result = create_test_result(
            question=question,
            answers=answers,
            api_info=api_info,
            formula=formula,
            ecosystem="Homebrew"
        )
        results.append(result)

        print(f"  ✓ 找到 {len(versions)} 个版本/变体")
        print(f"  版本: {versions}")

    save_result("code_ecosystem/homebrew", {
        "api_name": "Homebrew Formulae",
        "requires_auth": False,
        "config": {"formulae": formulae},
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
