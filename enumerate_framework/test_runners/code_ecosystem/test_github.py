"""GitHub API 完整测试 - 统一版本

合并以下功能：
1. 基础枚举 + 元数据过滤
2. Forked仓库枚举
3. Release/Branch/高级功能测试
"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from ..utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行GitHub API完整测试

    测试结构：
    Part 1 - 基础枚举 + 元数据过滤:
      - 列出所有仓库
      - Star>1000的仓库
      - 主语言为C的仓库
      - 2010年后创建的仓库

    Part 2 - 高级功能:
      - 列出所有forked仓库
      - 找出所有pre-release版本
      - 找出超过1年未更新的分支
      - 找出star最多的仓库
    """
    print_header("测试 GitHub API - 完整版（统一输出）")

    from fetchers.code_ecosystem.github import GitHubFetcher
    fetcher = GitHubFetcher()

    # 默认配置
    config = {
        "test_user": "torvalds",  # Linus Torvalds - Linux创始人
        "test_repo_releases": "nodejs/node",  # Node.js项目（有很多releases）
        "test_repo_branches": "rails/rails",  # Rails项目（有很多分支）
        "max_repos": 100,
        "max_releases": 100,
        "max_branches": 20
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    all_results = []
    username = config["test_user"]

    print(f"\n{'='*70}")
    print(f"测试用户: {username}")
    print(f"测试仓库 (Releases): {config['test_repo_releases']}")
    print(f"测试仓库 (Branches): {config['test_repo_branches']}")
    print(f"{'='*70}")

    # ========================================================================
    # PART 1: 基础枚举 + 元数据过滤
    # ========================================================================

    print(f"\n{'='*70}")
    print("PART 1: 基础枚举 + 元数据过滤")
    print(f"{'='*70}")

    # 1.1 基础问题：列出所有仓库
    print(f"\n[1.1] 列出所有仓库")
    repos_with_metadata, api_info, base_question = fetcher.fetch_repos_with_metadata(
        username=username,
        max_repos=config["max_repos"]
    )

    total_count = len(repos_with_metadata)
    print(f"  ✓ 找到 {total_count} 个仓库")
    print(f"  前3个:")
    for repo in repos_with_metadata[:3]:
        print(f"    - {repo['name']} (⭐ {repo['stars']}, 🍴 {repo['forks']}, {repo['language'] or 'N/A'})")

    all_results.append({
        "test_id": "1.1",
        "category": "基础枚举",
        "question": f"列出GitHub用户{username}的所有公开仓库",
        "total_count": total_count,
        "repositories": [
            {
                "name": r['name'],
                "stars": r['stars'],
                "forks": r['forks'],
                "language": r['language'],
                "created_at": r['created_at'][:10]
            } for r in repos_with_metadata
        ],
        "api_info": api_info
    })

    # 1.2 Star>1000的仓库
    print(f"\n[1.2] 列出star数超过1000的仓库")
    popular_repos = fetcher.filter_by_stars(repos_with_metadata, min_stars=1000)
    filtered_count = len(popular_repos)
    percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

    print(f"  ✓ 找到 {filtered_count} 个仓库（占比: {percentage:.1f}%）")
    for repo in popular_repos:
        print(f"    - {repo['name']}: ⭐ {repo['stars']:,}")

    all_results.append({
        "test_id": "1.2",
        "category": "元数据过滤",
        "question": f"列出GitHub用户{username}的所有仓库，其中star数超过1000的",
        "filter_type": "stars",
        "filter_value": {"min_stars": 1000},
        "total_count": filtered_count,
        "percentage": f"{percentage:.1f}%",
        "repositories": [
            {
                "name": r['name'],
                "stars": r['stars'],
                "language": r['language']
            } for r in popular_repos
        ]
    })

    # 1.3 主语言为C的仓库
    print(f"\n[1.3] 列出主语言为C的仓库")
    c_repos = fetcher.filter_by_language(repos_with_metadata, "C")
    filtered_count = len(c_repos)
    percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

    print(f"  ✓ 找到 {filtered_count} 个仓库（占比: {percentage:.1f}%）")
    for repo in c_repos[:5]:
        print(f"    - {repo['name']} (⭐ {repo['stars']})")

    all_results.append({
        "test_id": "1.3",
        "category": "元数据过滤",
        "question": f"列出GitHub用户{username}的所有仓库，其中主语言是C的",
        "filter_type": "language",
        "filter_value": "C",
        "total_count": filtered_count,
        "percentage": f"{percentage:.1f}%",
        "repositories": [
            {
                "name": r['name'],
                "stars": r['stars'],
                "created_at": r['created_at'][:10]
            } for r in c_repos
        ]
    })

    # 1.4 2010年后创建的仓库
    print(f"\n[1.4] 列出2010年后创建的仓库")
    recent_repos = fetcher.filter_by_created_date(repos_with_metadata, min_year=2010)
    filtered_count = len(recent_repos)
    percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

    print(f"  ✓ 找到 {filtered_count} 个仓库（占比: {percentage:.1f}%）")

    # 按年份统计
    from collections import defaultdict
    year_counts = defaultdict(int)
    for repo in recent_repos:
        if repo['created_at']:
            year = repo['created_at'][:4]
            year_counts[year] += 1

    print(f"  年份分布:")
    for year in sorted(year_counts.keys(), reverse=True)[:5]:
        print(f"    {year}: {year_counts[year]}个")

    all_results.append({
        "test_id": "1.4",
        "category": "元数据过滤",
        "question": f"列出GitHub用户{username}的所有仓库，其中在2010年后创建的",
        "filter_type": "created_date",
        "filter_value": {"min_year": 2010},
        "total_count": filtered_count,
        "percentage": f"{percentage:.1f}%",
        "year_distribution": dict(year_counts),
        "repositories": [
            {
                "name": r['name'],
                "created_at": r['created_at'][:10],
                "stars": r['stars']
            } for r in recent_repos
        ]
    })

    # ========================================================================
    # PART 2: 高级功能
    # ========================================================================

    print(f"\n{'='*70}")
    print("PART 2: 高级功能")
    print(f"{'='*70}")

    # 2.1 列出被fork数大于指定值的仓库
    min_forks_threshold = 100
    print(f"\n[2.1] 列出被fork数大于{min_forks_threshold}的仓库")
    print(f"  说明: 这需要知道每个仓库被别人fork的次数")

    highly_forked_repos = fetcher.filter_by_forks(repos_with_metadata, min_forks=min_forks_threshold)
    filtered_count = len(highly_forked_repos)
    percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

    print(f"  ✓ 找到 {filtered_count} 个仓库（占比: {percentage:.1f}%）")
    if highly_forked_repos:
        print(f"  仓库列表:")
        for repo in highly_forked_repos[:10]:
            print(f"    - {repo['name']}: {repo['forks']:,} forks, ⭐ {repo['stars']:,}")

    all_results.append({
        "test_id": "2.1",
        "category": "高级功能",
        "question": f"列出{username}用户所有仓库中，被fork数超过{min_forks_threshold}的",
        "filter_type": "forks",
        "filter_value": {"min_forks": min_forks_threshold},
        "total_count": filtered_count,
        "percentage": f"{percentage:.1f}%",
        "repositories": [
            {
                "name": r['name'],
                "forks": r['forks'],
                "stars": r['stars'],
                "language": r['language']
            } for r in highly_forked_repos
        ]
    })

    # 2.2 找出所有pre-release版本
    print(f"\n[2.2] 找出所有pre-release版本")
    print(f"  目标: {config['test_repo_releases']}")

    all_releases, api_info_releases, question_releases = fetcher.fetch_releases(
        config['test_repo_releases'],
        max_releases=config['max_releases'],
        include_metadata=True
    )

    print(f"  ✓ 找到 {len(all_releases)} 个releases")

    prereleases = fetcher.filter_prerelease(all_releases)
    percentage = (len(prereleases) / len(all_releases) * 100) if all_releases else 0

    print(f"  ✓ 其中 {len(prereleases)} 个是pre-release (占比: {percentage:.1f}%)")
    if prereleases:
        print(f"  示例:")
        for release in prereleases[:5]:
            print(f"    - {release['tag_name']}: {release['name']} (发布于 {release['published_at'][:10]})")

    all_results.append({
        "test_id": "2.2",
        "category": "高级功能",
        "question": f"列出{config['test_repo_releases']}仓库中所有pre-release版本",
        "total_releases": len(all_releases),
        "prerelease_count": len(prereleases),
        "percentage": f"{percentage:.1f}%",
        "prereleases": [
            {
                "tag_name": r['tag_name'],
                "name": r['name'],
                "published_at": r['published_at'][:10]
            } for r in prereleases[:20]
        ],
        "api_info": api_info_releases
    })

    # 2.3 找出超过1年未更新的分支
    print(f"\n[2.3] 找出超过1年未更新的分支")
    print(f"  目标: {config['test_repo_branches']}")
    print(f"  注意: 此操作需要额外API调用，可能较慢...")

    all_branches, api_info_branches, question_branches = fetcher.fetch_branches(
        config['test_repo_branches'],
        max_branches=config['max_branches'],
        include_metadata=True
    )

    print(f"  ✓ 找到 {len(all_branches)} 个分支")

    stale_branches = fetcher.filter_stale_branches(all_branches, months=12)
    percentage = (len(stale_branches) / len(all_branches) * 100) if all_branches else 0

    print(f"  ✓ 其中 {len(stale_branches)} 个超过1年未更新 (占比: {percentage:.1f}%)")
    if stale_branches:
        print(f"  示例:")
        for branch in stale_branches[:5]:
            print(f"    - {branch['name']}: 最后更新于 {branch['last_commit_date'][:10]}")

    all_results.append({
        "test_id": "2.3",
        "category": "高级功能",
        "question": f"列出{config['test_repo_branches']}仓库中超过1年未更新的分支",
        "total_branches": len(all_branches),
        "stale_count": len(stale_branches),
        "percentage": f"{percentage:.1f}%",
        "stale_branches": [
            {
                "name": b['name'],
                "last_commit_date": b['last_commit_date'][:10]
            } for b in stale_branches
        ],
        "api_info": api_info_branches
    })

    # 2.4 找出star最多的仓库
    print(f"\n[2.4] 找出star最多的仓库")
    most_starred = fetcher.get_most_starred_repo(repos_with_metadata)

    if most_starred:
        print(f"  ✓ Star最多的仓库:")
        print(f"    名称: {most_starred['name']}")
        print(f"    Stars: ⭐ {most_starred['stars']:,}")
        print(f"    语言: {most_starred['language'] or 'N/A'}")
        print(f"    创建于: {most_starred['created_at'][:10]}")

        # 显示Top 5
        sorted_repos = sorted(repos_with_metadata, key=lambda r: r['stars'], reverse=True)
        print(f"\n  Top 5仓库:")
        for i, repo in enumerate(sorted_repos[:5], 1):
            print(f"    {i}. {repo['name']}: ⭐ {repo['stars']:,}")

    all_results.append({
        "test_id": "2.4",
        "category": "高级功能",
        "question": f"找出{username}用户star最多的仓库",
        "most_starred": {
            "name": most_starred['name'],
            "stars": most_starred['stars'],
            "language": most_starred['language'],
            "created_at": most_starred['created_at'][:10]
        } if most_starred else None,
        "top_5": [
            {
                "rank": i + 1,
                "name": r['name'],
                "stars": r['stars'],
                "language": r['language']
            } for i, r in enumerate(sorted(repos_with_metadata, key=lambda r: r['stars'], reverse=True)[:5])
        ]
    })

    # ========================================================================
    # 保存统一结果
    # ========================================================================

    save_result("code_ecosystem/github", {
        "api_name": "GitHub",
        "description": "完整的GitHub API测试：基础枚举 + 元数据过滤 + 高级功能",
        "test_sections": [
            "基础枚举 + 元数据过滤 (4个测试)",
            "高级功能测试 (4个测试)"
        ],
        "requires_auth": False,
        "difficulty_level": "Advanced (Level 2)",
        "config": config,
        "summary": {
            "test_user": username,
            "total_repos": total_count,
            "popular_repos": len(popular_repos),
            "c_repos": len(c_repos),
            "recent_repos": len(recent_repos),
            "highly_forked_repos": len(highly_forked_repos),
            "total_releases": len(all_releases),
            "prereleases": len(prereleases),
            "total_branches": len(all_branches),
            "stale_branches": len(stale_branches),
            "most_starred": most_starred['name'] if most_starred else None
        },
        "tests": all_results
    })

    print(f"\n{'='*70}")
    print(f"✓ GitHub完整测试完成!")
    print(f"{'='*70}")
    print(f"\n总结:")
    print(f"  Part 1 - 基础枚举 + 元数据过滤:")
    print(f"    ✓ 总仓库数: {total_count}")
    print(f"    ✓ 高Star仓库 (>1000): {len(popular_repos)}")
    print(f"    ✓ C语言仓库: {len(c_repos)}")
    print(f"    ✓ 新建仓库 (2010+): {len(recent_repos)}")
    print(f"  Part 2 - 高级功能:")
    print(f"    ✓ 高Fork仓库 (>100): {len(highly_forked_repos)}")
    print(f"    ✓ Pre-releases: {len(prereleases)}/{len(all_releases)}")
    print(f"    ✓ 陈旧分支 (>1年): {len(stale_branches)}/{len(all_branches)}")
    print(f"    ✓ 最受欢迎: {most_starred['name'] if most_starred else 'N/A'}")
    print(f"\n结果已保存: output/api_tests/code_ecosystem/github.json")

    return all_results


if __name__ == "__main__":
    run()
