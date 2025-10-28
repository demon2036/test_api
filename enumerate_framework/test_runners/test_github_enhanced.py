"""GitHub API 增强测试 - 元数据过滤"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行GitHub API增强测试

    测试结构：
    - 1个基础问题：列出所有仓库
    - 3个增强问题：
      1. Star数>1000的仓库（元数据：star计数）
      2. 主语言为C的仓库（元数据：编程语言）
      3. 2010年后创建的仓库（元数据：创建日期）
    """
    print_header("测试 GitHub API - 基础 + 元数据增强")

    from fetchers.github import GitHubFetcher
    fetcher = GitHubFetcher()

    # 默认配置
    config = {
        "users": ["torvalds"],  # Linus Torvalds - Linux创始人
        "max_repos": 100
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    all_results = []

    for username in config["users"]:
        print(f"\n{'='*70}")
        print(f"测试用户: {username}")
        print(f"{'='*70}")

        # ==================== 基础问题 ====================
        print(f"\n[基础问题] 列出所有仓库")
        repos_with_metadata, api_info, base_question = fetcher.fetch_repos_with_metadata(
            username=username,
            max_repos=config["max_repos"]
        )

        total_count = len(repos_with_metadata)
        print(f"  ✓ 找到 {total_count} 个仓库")
        print(f"  前3个:")
        for repo in repos_with_metadata[:3]:
            print(f"    - {repo['name']} (⭐ {repo['stars']}, {repo['language'] or 'N/A'})")

        base_result = {
            "question": f"列出GitHub用户{username}的所有公开仓库",
            "total_count": total_count,
            "repositories": [
                {
                    "name": r['name'],
                    "stars": r['stars'],
                    "language": r['language'],
                    "created_at": r['created_at'][:10]  # 只保留日期部分
                } for r in repos_with_metadata
            ]
        }

        # ==================== 增强问题 1：Star>1000 ====================
        print(f"\n[增强问题 1/3] 列出star数超过1000的仓库")
        print(f"  说明: 这需要知道每个仓库的star数")

        popular_repos = fetcher.filter_by_stars(repos_with_metadata, min_stars=1000)

        filtered_count = len(popular_repos)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个仓库（占比: {percentage:.1f}%）")
        print(f"  仓库列表:")
        for repo in popular_repos:
            print(f"    - {repo['name']}: ⭐ {repo['stars']:,}")

        enhanced_result_1 = {
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
        }

        # ==================== 增强问题 2：语言为C ====================
        print(f"\n[增强问题 2/3] 列出主语言为C的仓库")
        print(f"  说明: 这需要知道每个仓库的主要编程语言")

        c_repos = fetcher.filter_by_language(repos_with_metadata, "C")

        filtered_count = len(c_repos)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 个仓库（占比: {percentage:.1f}%）")
        print(f"  前5个:")
        for repo in c_repos[:5]:
            print(f"    - {repo['name']} (⭐ {repo['stars']})")

        enhanced_result_2 = {
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
        }

        # ==================== 增强问题 3：2010年后创建 ====================
        print(f"\n[增强问题 3/3] 列出2010年后创建的仓库")
        print(f"  说明: 这需要知道每个仓库的创建日期")

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

        enhanced_result_3 = {
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
        }

        # ==================== 汇总结果 ====================
        user_result = {
            "username": username,
            "base_test": base_result,
            "enhanced_tests": [
                enhanced_result_1,
                enhanced_result_2,
                enhanced_result_3
            ],
            "api_info": api_info,
            "summary": {
                "total_repos": total_count,
                "popular_repos": len(popular_repos),
                "c_repos": len(c_repos),
                "recent_repos": len(recent_repos)
            }
        }

        all_results.append(user_result)

    # 保存结果
    save_result("github_enhanced", {
        "api_name": "GitHub (Enhanced with Metadata Filtering)",
        "description": "测试AI的深度枚举能力：不仅要列举所有仓库，还要根据元数据过滤",
        "requires_auth": False,
        "difficulty_level": "Advanced (Level 2)",
        "config": config,
        "tests": all_results
    })

    print(f"\n{'='*70}")
    print(f"✓ GitHub增强测试完成!")
    print(f"{'='*70}")
    print(f"\n结果已保存: output/api_tests/github_enhanced.json")

    return all_results


if __name__ == "__main__":
    run()
