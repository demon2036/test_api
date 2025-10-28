#!/usr/bin/env python3
"""验证脚本 - 验证API可访问性"""

import json
import requests


def verify_api_access(filepath: str = "output/test_cases.json"):
    """验证所有API是否可访问"""

    with open(filepath, "r") as f:
        test_cases = json.load(f)

    print("=" * 80)
    print("验证API可访问性")
    print("=" * 80)

    success = 0
    failed = 0

    for tc in test_cases:
        domain = tc['domain']
        api_info = tc['api_info']

        try:
            response = requests.get(
                api_info['api_endpoint'],
                params=api_info.get('parameters', {}),
                timeout=10
            )

            if response.status_code == 200:
                print(f"✓ {domain}")
                success += 1
            else:
                print(f"✗ {domain} (状态码: {response.status_code})")
                failed += 1

        except Exception as e:
            print(f"✗ {domain} (错误: {str(e)[:50]})")
            failed += 1

    print("\n" + "=" * 80)
    print(f"结果: {success} 成功, {failed} 失败")
    print("=" * 80)


if __name__ == '__main__':
    verify_api_access()
