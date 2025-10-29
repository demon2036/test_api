"""PubMed API 增强测试 - 元数据过滤"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from ..utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行PubMed API增强测试

    测试结构：
    - 1个基础问题：列出所有出版物
    - 3个增强问题：
      1. 作为通讯作者的论文（元数据：作者角色）
      2. Review类型的文章（元数据：文章类型）
      3. 特定期刊的论文（元数据：期刊名称）
    """
    print_header("测试 PubMed API - 基础 + 元数据增强")

    from fetchers.academic_research.pubmed import PubMedFetcher
    fetcher = PubMedFetcher()

    # 默认配置 - 使用知名研究者的ORCID
    config = {
        "researchers": [
            {"orcid": "0000-0003-0799-4776", "name": "Anthony S. Fauci"},
        ],
        "max_results": 1000  # 限制以加快测试
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    all_results = []

    for researcher in config["researchers"]:
        orcid = researcher["orcid"]
        name = researcher["name"]

        print(f"\n{'='*70}")
        print(f"测试研究者: {name} (ORCID: {orcid})")
        print(f"{'='*70}")

        # ==================== 基础问题 ====================
        print(f"\n[基础问题] 列出所有出版物")
        pubs_with_metadata, api_info, base_question = fetcher.fetch_by_orcid_with_metadata(
            orcid=orcid,
            max_results=config["max_results"]
        )

        total_count = len(pubs_with_metadata)
        print(f"  ✓ 找到 {total_count} 篇出版物")
        print(f"  前3篇:")
        for pub in pubs_with_metadata[:3]:
            year = pub.get('year', 'N/A')
            title = pub.get('title', 'Unknown')[:80]
            print(f"    - [{year}] {title}...")

        # 保存基础结果
        base_result = {
            "question": base_question,
            "total_count": total_count,
            "publications": [
                {
                    "pmid": p.get('pmid'),
                    "title": p.get('title'),
                    "year": p.get('year'),
                    "journal": p.get('journal'),
                    "article_types": p.get('article_types', [])
                } for p in pubs_with_metadata
            ],
            "metadata_available": True
        }

        # ==================== 增强问题 1：通讯作者 ====================
        print(f"\n[增强问题 1/3] 列出作为通讯作者的所有出版物")
        print(f"  说明: 这需要知道每篇论文的作者列表和通讯作者标记")

        corresponding_pubs = fetcher.filter_by_author_role(pubs_with_metadata, 'corresponding')

        filtered_count = len(corresponding_pubs)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 篇（占比: {percentage:.1f}%）")
        print(f"  前3篇:")
        for pub in corresponding_pubs[:3]:
            year = pub.get('year', 'N/A')
            title = pub.get('title', 'Unknown')[:60]
            journal = pub.get('journal', 'Unknown')[:30]
            print(f"    - [{year}] {title}...")
            print(f"      期刊: {journal}")

        enhanced_result_1 = {
            "question": f"列出PubMed中{name} (ORCID: {orcid})作为通讯作者的所有出版物",
            "filter_type": "author_role",
            "filter_value": "corresponding",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "publications": [
                {
                    "pmid": p.get('pmid'),
                    "title": p.get('title'),
                    "year": p.get('year'),
                    "journal": p.get('journal'),
                    "authors": [a.get('name') for a in p.get('authors', [])][:5]  # 只保留前5位作者
                } for p in corresponding_pubs
            ]
        }

        # ==================== 增强问题 2：Review文章 ====================
        print(f"\n[增强问题 2/3] 列出所有Review类型的文章")
        print(f"  说明: 这需要知道每篇论文的文章类型（Review, Meta-Analysis等）")

        review_pubs = fetcher.filter_by_article_type(pubs_with_metadata, "Review")

        filtered_count = len(review_pubs)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 篇（占比: {percentage:.1f}%）")
        print(f"  前3篇:")
        for pub in review_pubs[:3]:
            year = pub.get('year', 'N/A')
            title = pub.get('title', 'Unknown')[:70]
            types = ', '.join(pub.get('article_types', []))
            print(f"    - [{year}] {title}...")
            print(f"      类型: {types}")

        enhanced_result_2 = {
            "question": f"列出PubMed中{name} (ORCID: {orcid})发表的所有Review类型文章",
            "filter_type": "article_type",
            "filter_value": "Review",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "publications": [
                {
                    "pmid": p.get('pmid'),
                    "title": p.get('title'),
                    "year": p.get('year'),
                    "article_types": p.get('article_types', []),
                    "journal": p.get('journal')
                } for p in review_pubs
            ]
        }

        # ==================== 增强问题 3：特定期刊 ====================
        # 选择一个该作者发表较多的期刊
        from collections import Counter
        journal_counts = Counter()
        for pub in pubs_with_metadata:
            journal = pub.get('journal', '')
            if journal:
                journal_counts[journal] += 1

        # 获取发表最多的期刊
        if journal_counts:
            top_journal = journal_counts.most_common(1)[0][0]
        else:
            top_journal = "Nature"  # 默认值

        print(f"\n[增强问题 3/3] 列出发表在期刊 '{top_journal}' 的所有出版物")
        print(f"  说明: 这需要知道每篇论文的期刊名称")

        journal_pubs = fetcher.filter_by_journal(pubs_with_metadata, top_journal)

        filtered_count = len(journal_pubs)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 篇（占比: {percentage:.1f}%）")
        print(f"  前3篇:")
        for pub in journal_pubs[:3]:
            year = pub.get('year', 'N/A')
            title = pub.get('title', 'Unknown')[:70]
            print(f"    - [{year}] {title}...")

        # 按年份分组统计
        from collections import defaultdict
        year_counts = defaultdict(int)
        for pub in journal_pubs:
            year = pub.get('year')
            if year:
                year_counts[year] += 1

        print(f"  年份分布:")
        for year in sorted(year_counts.keys(), reverse=True)[:5]:  # 显示最近5年
            print(f"    {year}: {year_counts[year]}篇")

        enhanced_result_3 = {
            "question": f"列出PubMed中{name} (ORCID: {orcid})在期刊'{top_journal}'发表的所有出版物",
            "filter_type": "journal",
            "filter_value": top_journal,
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "year_distribution": dict(year_counts),
            "publications": [
                {
                    "pmid": p.get('pmid'),
                    "title": p.get('title'),
                    "year": p.get('year'),
                    "article_types": p.get('article_types', [])
                } for p in journal_pubs
            ]
        }

        # ==================== 汇总结果 ====================
        researcher_result = {
            "researcher": name,
            "orcid": orcid,
            "base_test": base_result,
            "enhanced_tests": [
                enhanced_result_1,
                enhanced_result_2,
                enhanced_result_3
            ],
            "api_info": api_info,
            "summary": {
                "total_publications": total_count,
                "as_corresponding_author": len(corresponding_pubs),
                "review_articles": len(review_pubs),
                "in_top_journal": len(journal_pubs),
                "top_journal": top_journal
            }
        }

        all_results.append(researcher_result)

    # 保存结果
    save_result("pubmed_enhanced", {
        "api_name": "PubMed (Enhanced with Metadata Filtering)",
        "description": "测试AI的深度枚举能力：不仅要列举所有项目，还要根据元数据过滤",
        "requires_auth": False,
        "difficulty_level": "Advanced (Level 2)",
        "config": config,
        "tests": all_results
    })

    print(f"\n{'='*70}")
    print(f"✓ PubMed增强测试完成!")
    print(f"{'='*70}")
    print(f"\n测试难度提升：")
    print(f"  Level 1 (基础): 列举所有出版物")
    print(f"  Level 2 (增强): 列举并过滤 - 需要理解每篇论文的详细元数据")
    print(f"\n结果已保存: output/api_tests/pubmed_enhanced.json")

    return all_results


if __name__ == "__main__":
    run()
