"""crt.sh 证书透明度 API 测试"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行crt.sh API测试

    Args:
        test_config: 测试配置字典，可包含:
            - domains: 要测试的域名列表
            - max_certs: 每个域名最多获取多少证书
    """
    print_header("测试 crt.sh 证书透明度 API")

    from fetchers.crtsh import CrtShFetcher
    fetcher = CrtShFetcher()

    # 默认配置
    config = {
        "domains": ['github.com', 'google.com', 'facebook.com'],
        "max_certs": 1000
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    for domain in config["domains"]:
        print(f"\n测试域名: {domain}")
        certs, api_info, question = fetcher.fetch(domain=domain, max_certs=config["max_certs"])

        result = create_test_result(
            identifier=domain,
            question=question,
            api_info=api_info,
            data=certs,
            data_key="certificates",
            domain=domain
        )
        results.append(result)

        print(f"  ✓ 找到 {len(certs)} 个证书/子域名")
        if len(certs) > 0:
            print(f"  前5个: {certs[:5]}")

    save_result("crtsh", {
        "api_name": "crt.sh",
        "requires_auth": False,
        "config": config,
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
