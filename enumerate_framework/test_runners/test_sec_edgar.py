"""SEC EDGAR API 测试"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行SEC EDGAR API测试

    Args:
        test_config: 测试配置字典，可包含:
            - companies: 要测试的公司列表（格式：[{"cik": "320193", "name": "Apple Inc."}, ...]）
            - max_filings: 每个公司最多获取多少文件
    """
    print_header("测试 SEC EDGAR API")

    from fetchers.sec_edgar import SECEdgarFetcher
    fetcher = SECEdgarFetcher()

    # 默认配置
    config = {
        "companies": [
            {"cik": "320193", "name": "Apple Inc."},
            {"cik": "789019", "name": "Microsoft Corp."}
        ],
        "max_filings": 1000
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    for company_info in config["companies"]:
        cik = company_info["cik"]
        company_name = company_info.get("name", cik)

        print(f"\n测试公司: CIK {cik} ({company_name})")
        filings, api_info, question = fetcher.fetch_company_filings(
            cik,
            max_filings=config["max_filings"]
        )

        result = create_test_result(
            identifier=cik,
            question=question,
            api_info=api_info,
            data=filings,
            data_key="filings",
            cik=cik,
            company_name=company_name
        )
        results.append(result)

        print(f"  ✓ 找到 {len(filings)} 个文件提交")
        if len(filings) > 0:
            print(f"  最近5个: {filings[:5]}")

    save_result("sec_edgar", {
        "api_name": "SEC EDGAR",
        "requires_auth": False,
        "config": config,
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
