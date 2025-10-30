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
    from test_runners.code_ecosystem.code_utils import calculate_percentage
    from test_runners.code_ecosystem.test_configs import get_github_config
else:
    from ..utils import save_result, create_test_result, print_header
    from .code_utils import calculate_percentage
    from .test_configs import get_github_config


def _format_repo(repo, rank=None):
    """Standardize repository metadata payload."""
    formatted = {
        "answer": repo.get('name'),
        "stars": repo.get('stars'),
        "forks": repo.get('forks'),
        "language": repo.get('language'),
        "created_at": repo.get('created_at')[:10] if repo.get('created_at') else None,
        "is_fork": repo.get('is_fork', False)
    }
    if rank is not None:
        formatted["rank"] = rank
    return formatted


def _format_release(release):
    """Standardize release metadata payload."""
    published_at = release.get('published_at')
    return {
        "answer": release.get('tag_name'),
        "name": release.get('name'),
        "published_at": published_at[:10] if isinstance(published_at, str) and published_at else None,
        "prerelease": release.get('prerelease', False)
    }


def _format_branch(branch):
    """Standardize branch metadata payload."""
    last_commit = branch.get('last_commit_date')
    return {
        "answer": branch.get('name'),
        "last_commit_date": last_commit[:10] if isinstance(last_commit, str) and last_commit else None
    }


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

    # 加载配置（从test_configs）
    if test_config:
        config = test_config
    else:
        config = get_github_config()

    tests = []

    print(f"\n{'='*70}")
    print(f"配置: {len(config['users'])} 个用户, "
          f"{len(config['release_repos'])} 个release仓库, "
          f"{len(config['branch_repos'])} 个branch仓库")
    print(f"{'='*70}")

    # 由于原测试逻辑是针对单用户的，我们取第一个用户来保持兼容性
    username = config["users"][0]["username"]
    test_repo_releases = config["release_repos"][0]["repo"]
    test_repo_branches = config["branch_repos"][0]["repo"]

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
        max_repos=config["max_items"]
    )

    total_count = len(repos_with_metadata)
    print(f"  ✓ 找到 {total_count} 个仓库")
    print(f"  前3个:")
    for repo in repos_with_metadata[:3]:
        print(f"    - {repo['name']} (⭐ {repo['stars']}, 🍴 {repo['forks']}, {repo['language'] or 'N/A'})")

    base_answers = [_format_repo(r) for r in repos_with_metadata]
    base_result = create_test_result(
        question=base_question,
        answers=base_answers,
        api_info=api_info,
        test_id="1.1",
        category="基础枚举",
        username=username,
        query_category="base_enumeration"
    )
    tests.append(base_result)

    # 1.2 Star>1000的仓库
    print(f"\n[1.2] 列出star数超过1000的仓库")
    popular_repos = fetcher.filter_by_stars(repos_with_metadata, min_stars=1000)
    filtered_count = len(popular_repos)
    percentage = calculate_percentage(filtered_count, total_count)

    print(f"  ✓ 找到 {filtered_count} 个仓库（占比: {percentage:.1f}%）")
    for repo in popular_repos:
        print(f"    - {repo['name']}: ⭐ {repo['stars']:,}")

    popular_answers = [_format_repo(r) for r in popular_repos]
    tests.append(create_test_result(
        question=f"列出GitHub用户{username}的所有仓库，其中star数超过1000的",
        answers=popular_answers,
        test_id="1.2",
        category="元数据过滤",
        filter={"stars": {"min": 1000}},
        match_percentage=f"{percentage:.1f}%",
        username=username
    ))

    # 1.3 主语言为C的仓库
    print(f"\n[1.3] 列出主语言为C的仓库")
    c_repos = fetcher.filter_by_language(repos_with_metadata, "C")
    filtered_count = len(c_repos)
    percentage = calculate_percentage(filtered_count, total_count)

    print(f"  ✓ 找到 {filtered_count} 个仓库（占比: {percentage:.1f}%）")
    for repo in c_repos[:5]:
        print(f"    - {repo['name']} (⭐ {repo['stars']})")

    c_repo_answers = [_format_repo(r) for r in c_repos]
    tests.append(create_test_result(
        question=f"列出GitHub用户{username}的所有仓库，其中主语言是C的",
        answers=c_repo_answers,
        test_id="1.3",
        category="元数据过滤",
        filter={"language": "C"},
        match_percentage=f"{percentage:.1f}%",
        username=username
    ))

    # 1.4 2010年后创建的仓库
    print(f"\n[1.4] 列出2010年后创建的仓库")
    recent_repos = fetcher.filter_by_created_date(repos_with_metadata, min_year=2010)
    filtered_count = len(recent_repos)
    percentage = calculate_percentage(filtered_count, total_count)

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

    recent_repo_answers = [_format_repo(r) for r in recent_repos]
    tests.append(create_test_result(
        question=f"列出GitHub用户{username}的所有仓库，其中在2010年后创建的",
        answers=recent_repo_answers,
        test_id="1.4",
        category="元数据过滤",
        filter={"created_after": 2010},
        match_percentage=f"{percentage:.1f}%",
        year_distribution=dict(year_counts),
        username=username
    ))

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
    percentage = calculate_percentage(filtered_count, total_count)

    print(f"  ✓ 找到 {filtered_count} 个仓库（占比: {percentage:.1f}%）")
    if highly_forked_repos:
        print(f"  仓库列表:")
        for repo in highly_forked_repos[:10]:
            print(f"    - {repo['name']}: {repo['forks']:,} forks, ⭐ {repo['stars']:,}")

    highly_forked_answers = [_format_repo(r) for r in highly_forked_repos]
    tests.append(create_test_result(
        question=f"列出{username}用户所有仓库中，被fork数超过{min_forks_threshold}的",
        answers=highly_forked_answers,
        test_id="2.1",
        category="高级功能",
        filter={"forks": {"min": min_forks_threshold}},
        match_percentage=f"{percentage:.1f}%",
        username=username
    ))

    # 2.2 找出所有pre-release版本
    print(f"\n[2.2] 找出所有pre-release版本")
    print(f"  目标: {test_repo_releases}")

    all_releases, api_info_releases, question_releases = fetcher.fetch_releases(
        test_repo_releases,
        max_releases=config['max_items'],
        include_metadata=True
    )

    print(f"  ✓ 找到 {len(all_releases)} 个releases")

    prereleases = fetcher.filter_prerelease(all_releases)
    percentage = calculate_percentage(len(prereleases), len(all_releases))

    print(f"  ✓ 其中 {len(prereleases)} 个是pre-release (占比: {percentage:.1f}%)")
    if prereleases:
        print(f"  示例:")
        for release in prereleases[:5]:
            print(f"    - {release['tag_name']}: {release['name']} (发布于 {release['published_at'][:10]})")

    prerelease_answers = [_format_release(r) for r in prereleases]
    tests.append(create_test_result(
        question=f"列出{test_repo_releases}仓库中所有pre-release版本",
        answers=prerelease_answers,
        api_info=api_info_releases,
        test_id="2.2",
        category="高级功能",
        repository=test_repo_releases,
        filter="prerelease=True",
        match_percentage=f"{percentage:.1f}%",
        total_releases=len(all_releases)
    ))

    # 2.3 找出超过1年未更新的分支
    print(f"\n[2.3] 找出超过1年未更新的分支")
    print(f"  目标: {test_repo_branches}")
    print(f"  注意: 此操作需要额外API调用，可能较慢...")

    all_branches, api_info_branches, question_branches = fetcher.fetch_branches(
        test_repo_branches,
        max_branches=20,  # 限制数量避免太慢
        include_metadata=True
    )

    print(f"  ✓ 找到 {len(all_branches)} 个分支")

    stale_branches = fetcher.filter_stale_branches(all_branches, months=12)
    percentage = calculate_percentage(len(stale_branches), len(all_branches))

    print(f"  ✓ 其中 {len(stale_branches)} 个超过1年未更新 (占比: {percentage:.1f}%)")
    if stale_branches:
        print(f"  示例:")
        for branch in stale_branches[:5]:
            print(f"    - {branch['name']}: 最后更新于 {branch['last_commit_date'][:10]}")

    stale_branch_answers = [_format_branch(b) for b in stale_branches]
    tests.append(create_test_result(
        question=f"列出{test_repo_branches}仓库中超过1年未更新的分支",
        answers=stale_branch_answers,
        api_info=api_info_branches,
        test_id="2.3",
        category="高级功能",
        repository=test_repo_branches,
        filter="last_update>12_months",
        match_percentage=f"{percentage:.1f}%",
        total_branches=len(all_branches)
    ))

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

    top_sorted = sorted(repos_with_metadata, key=lambda r: r['stars'], reverse=True)
    top_answers = [_format_repo(repo, rank=i + 1) for i, repo in enumerate(top_sorted[:5])]
    highlight_answer = top_answers[0] if top_answers else None
    tests.append(create_test_result(
        question=f"找出{username}用户star最多的仓库",
        answers=top_answers,
        test_id="2.4",
        category="高级功能",
        username=username,
        highlight_answer=highlight_answer
    ))

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
        "tests": tests
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

    return tests


if __name__ == "__main__":
    run()
