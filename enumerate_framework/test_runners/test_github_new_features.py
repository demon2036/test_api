"""GitHub API 新功能测试 - 根据GEMINI.md TODO实现"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, print_header
else:
    from .utils import save_result, print_header


def run(test_config=None):
    """运行GitHub新功能测试

    测试GEMINI.md中TODO功能：
    1. 列出所有forked仓库
    2. 找出pre-release版本
    3. 找出超过1年未更新的分支
    4. 找出star最多的仓库
    """
    print_header("测试 GitHub API - 新功能 (GEMINI.md TODO)")

    from fetchers.github import GitHubFetcher
    fetcher = GitHubFetcher()

    # 默认配置
    config = {
        "test_user": "torvalds",  # Linus Torvalds
        "test_repo": "nodejs/node",  # Node.js项目（有很多releases）
        "test_repo_branches": "rails/rails",  # Rails项目（有很多分支）
        "max_items": 100
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    all_results = []

    print(f"\n{'='*70}")
    print(f"测试对象: {config['test_user']}, {config['test_repo']}, {config['test_repo_branches']}")
    print(f"{'='*70}")

    # ==================== TODO 1: 列出所有forked仓库 ====================
    print(f"\n[TODO 1] 列出用户的所有forked仓库")
    print(f"  目标: {config['test_user']}")

    forked_repos, api_info_1, question_1 = fetcher.fetch_forked_repos(
        config['test_user'],
        max_repos=config['max_items']
    )

    print(f"  ✓ 找到 {len(forked_repos)} 个forked仓库")
    if forked_repos:
        print(f"  示例:")
        for repo in forked_repos[:5]:
            print(f"    - {repo}")

    all_results.append({
        "todo_id": 1,
        "feature": "fetch_forked_repos",
        "question": question_1,
        "test_case": f"用户 {config['test_user']} 的所有forked仓库",
        "total_count": len(forked_repos),
        "sample_data": forked_repos[:10],
        "api_info": api_info_1
    })

    # ==================== TODO 2: 找出所有pre-release版本 ====================
    print(f"\n[TODO 2] 找出所有pre-release版本")
    print(f"  目标: {config['test_repo']}")

    # 先获取所有releases（带元数据）
    all_releases, api_info_2, question_2 = fetcher.fetch_releases(
        config['test_repo'],
        max_releases=config['max_items'],
        include_metadata=True
    )

    print(f"  ✓ 找到 {len(all_releases)} 个releases")

    # 过滤出pre-release
    prereleases = fetcher.filter_prerelease(all_releases)
    percentage = (len(prereleases) / len(all_releases) * 100) if all_releases else 0

    print(f"  ✓ 其中 {len(prereleases)} 个是pre-release (占比: {percentage:.1f}%)")
    if prereleases:
        print(f"  示例:")
        for release in prereleases[:5]:
            print(f"    - {release['tag_name']}: {release['name']} (发布于 {release['published_at'][:10]})")

    all_results.append({
        "todo_id": 2,
        "feature": "filter_prerelease",
        "question": f"列出{config['test_repo']}仓库中所有pre-release版本",
        "test_case": f"{config['test_repo']} 的pre-release版本",
        "total_releases": len(all_releases),
        "prerelease_count": len(prereleases),
        "percentage": f"{percentage:.1f}%",
        "sample_data": [
            {
                "tag_name": r['tag_name'],
                "name": r['name'],
                "published_at": r['published_at'][:10]
            } for r in prereleases[:10]
        ],
        "api_info": api_info_2
    })

    # ==================== TODO 3: 找出超过1年未更新的分支 ====================
    print(f"\n[TODO 3] 找出超过1年未更新的分支")
    print(f"  目标: {config['test_repo_branches']}")
    print(f"  注意: 此操作需要额外API调用，可能较慢...")

    # 获取所有分支（带元数据）
    all_branches, api_info_3, question_3 = fetcher.fetch_branches(
        config['test_repo_branches'],
        max_branches=20,  # 限制数量避免太慢
        include_metadata=True
    )

    print(f"  ✓ 找到 {len(all_branches)} 个分支（限制20个以加快测试）")

    # 过滤出超过12个月未更新的分支
    stale_branches = fetcher.filter_stale_branches(all_branches, months=12)
    percentage = (len(stale_branches) / len(all_branches) * 100) if all_branches else 0

    print(f"  ✓ 其中 {len(stale_branches)} 个超过1年未更新 (占比: {percentage:.1f}%)")
    if stale_branches:
        print(f"  示例:")
        for branch in stale_branches[:5]:
            print(f"    - {branch['name']}: 最后更新于 {branch['last_commit_date'][:10]}")

    all_results.append({
        "todo_id": 3,
        "feature": "filter_stale_branches",
        "question": f"列出{config['test_repo_branches']}仓库中超过1年未更新的分支",
        "test_case": f"{config['test_repo_branches']} 的陈旧分支",
        "total_branches": len(all_branches),
        "stale_count": len(stale_branches),
        "percentage": f"{percentage:.1f}%",
        "sample_data": [
            {
                "name": b['name'],
                "last_commit_date": b['last_commit_date'][:10]
            } for b in stale_branches[:10]
        ],
        "api_info": api_info_3
    })

    # ==================== TODO 4: 找出star最多的仓库 ====================
    print(f"\n[TODO 4] 找出star最多的仓库")
    print(f"  目标: {config['test_user']}")

    # 获取所有仓库（带元数据）
    all_repos, api_info_4, question_4 = fetcher.fetch_repos_with_metadata(
        config['test_user'],
        max_repos=config['max_items']
    )

    print(f"  ✓ 找到 {len(all_repos)} 个仓库")

    # 找出star最多的仓库
    most_starred = fetcher.get_most_starred_repo(all_repos)

    if most_starred:
        print(f"  ✓ Star最多的仓库:")
        print(f"    名称: {most_starred['name']}")
        print(f"    Stars: ⭐ {most_starred['stars']:,}")
        print(f"    语言: {most_starred['language'] or 'N/A'}")
        print(f"    创建于: {most_starred['created_at'][:10]}")

        # 显示Top 5
        sorted_repos = sorted(all_repos, key=lambda r: r['stars'], reverse=True)
        print(f"\n  Top 5仓库:")
        for i, repo in enumerate(sorted_repos[:5], 1):
            print(f"    {i}. {repo['name']}: ⭐ {repo['stars']:,}")

    all_results.append({
        "todo_id": 4,
        "feature": "get_most_starred_repo",
        "question": f"找出{config['test_user']}用户star最多的仓库",
        "test_case": f"{config['test_user']} 的最受欢迎仓库",
        "total_repos": len(all_repos),
        "most_starred": {
            "name": most_starred['name'],
            "stars": most_starred['stars'],
            "language": most_starred['language'],
            "created_at": most_starred['created_at'][:10]
        } if most_starred else None,
        "top_5": [
            {
                "name": r['name'],
                "stars": r['stars'],
                "language": r['language']
            } for r in sorted(all_repos, key=lambda r: r['stars'], reverse=True)[:5]
        ],
        "api_info": api_info_4
    })

    # ==================== 保存结果 ====================
    save_result("github_new_features", {
        "api_name": "GitHub (New Features from GEMINI.md TODO)",
        "description": "测试根据GEMINI.md TODO列表实现的新功能",
        "implemented_todos": [
            "列出所有forked仓库",
            "找出所有pre-release版本",
            "找出超过1年未更新的分支",
            "找出star最多的仓库"
        ],
        "requires_auth": False,
        "config": config,
        "tests": all_results
    })

    print(f"\n{'='*70}")
    print(f"✓ GitHub新功能测试完成!")
    print(f"{'='*70}")
    print(f"\n总结:")
    print(f"  ✓ TODO 1 - Forked仓库: {all_results[0]['total_count']} 个")
    print(f"  ✓ TODO 2 - Pre-release: {all_results[1]['prerelease_count']}/{all_results[1]['total_releases']} 个")
    print(f"  ✓ TODO 3 - 陈旧分支: {all_results[2]['stale_count']}/{all_results[2]['total_branches']} 个")
    print(f"  ✓ TODO 4 - 最受欢迎: {all_results[3]['most_starred']['name'] if all_results[3]['most_starred'] else 'N/A'}")
    print(f"\n结果已保存: output/api_tests/github_new_features.json")

    return all_results


if __name__ == "__main__":
    run()
