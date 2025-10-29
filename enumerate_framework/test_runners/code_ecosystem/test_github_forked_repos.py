"""GitHub Forked Repos API 测试"""

import time
import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, print_header
else:
    from ..utils import save_result, print_header


def run(test_config=None):
    """运行GitHub Forked Repos API测试

    Args:
        test_config: 测试配置字典，可包含:
            - users: 要测试的用户列表
            - max_repos: 每个用户最多获取多少forked仓库
    """
    print_header("测试 GitHub Forked Repos API")

    from fetchers.code_ecosystem.github import GitHubFetcher
    fetcher = GitHubFetcher()

    # 默认配置
    config = {
        "users": ['torvalds', 'gvanrossum'],
        "max_repos": 1000
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    # 测试用户forked仓库
    for user in config["users"]:
        print(f"\n测试用户forked仓库: {user}")
        forked_repos, api_info, question = fetcher.fetch_forked_repos(user, max_repos=config["max_repos"])

        results.append({
            "type": "forked_repos",
            "username": user,
            "question": question,
            "api_info": api_info,
            "total_forked_repos": len(forked_repos),
            "forked_repos": forked_repos
        })
        print(f"  ✓ 找到 {len(forked_repos)} 个forked仓库")
        time.sleep(1)

    save_result("code_ecosystem/github_forked_repos", {
        "api_name": "GitHub Forked Repos",
        "requires_auth": False,
        "note": "未认证速率限制: 60 req/hour",
        "config": config,
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
