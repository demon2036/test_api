"""GitHub API 测试"""

import time
import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, print_header
else:
    from .utils import save_result, print_header


def run(test_config=None):
    """运行GitHub API测试

    Args:
        test_config: 测试配置字典，可包含:
            - users: 要测试的用户列表
            - repos_for_tags: 要测试tags的仓库列表
            - max_repos: 每个用户最多获取多少仓库
            - max_tags: 每个仓库最多获取多少标签
    """
    print_header("测试 GitHub API")

    from fetchers.github import GitHubFetcher
    fetcher = GitHubFetcher()

    # 默认配置
    config = {
        "users": ['torvalds', 'gvanrossum'],
        "repos_for_tags": ['torvalds/linux', 'python/cpython'],
        "max_repos": 1000,
        "max_tags": 1000
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    # 测试用户仓库
    for user in config["users"]:
        print(f"\n测试用户仓库: {user}")
        repos, api_info, question = fetcher.fetch_repos(user, max_repos=config["max_repos"])

        results.append({
            "type": "repos",
            "username": user,
            "question": question,
            "api_info": api_info,
            "total_repos": len(repos),
            "repos": repos
        })
        print(f"  ✓ 找到 {len(repos)} 个仓库")
        time.sleep(1)

    # 测试仓库标签
    for repo in config["repos_for_tags"]:
        print(f"\n测试仓库标签: {repo}")
        tags, api_info, question = fetcher.fetch_tags(repo, max_tags=config["max_tags"])

        results.append({
            "type": "tags",
            "repo": repo,
            "question": question,
            "api_info": api_info,
            "total_tags": len(tags),
            "sample_tags": tags[:20] if len(tags) > 20 else tags
        })
        print(f"  ✓ 找到 {len(tags)} 个标签")
        time.sleep(1)

    save_result("github", {
        "api_name": "GitHub",
        "requires_auth": False,
        "note": "未认证速率限制: 60 req/hour",
        "config": config,
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
