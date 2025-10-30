"""PubMed API 测试运行器 - 基础枚举 + 元数据增强查询"""

import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from ...utils import save_result, create_test_result, print_header


def _format_publication(pub, index_map):
    """规范化PubMed出版物输出，保留核心元数据"""
    idx = index_map.get(id(pub), -1)
    return {
        "rank": idx + 1 if idx >= 0 else None,
        "pmid": pub.get("pmid"),
        "title": pub.get("title"),
        "year": pub.get("year"),
        "journal": pub.get("journal"),
        "article_types": pub.get("article_types", []),
        "doi": pub.get("doi"),
        "authors": pub.get("authors", []),
    }


def run(test_config=None):
    """运行PubMed API测试，统一提供基础枚举与元数据增强题目"""
    print_header("测试 PubMed API (基础 + 元数据增强)")

    from fetchers.academic_research.pubmed import PubMedFetcher

    fetcher = PubMedFetcher()

    # 默认配置 - 使用ORCID以保证精确性
    config = {
        "researchers": [
            {"orcid": "0000-0003-0799-4776", "name": "Anthony S. Fauci"},
        ],
        "max_results": 1000,
        "sleep_seconds": 1.0,
    }

    if test_config:
        config.update(test_config)

    all_results = []

    print("\n说明:")
    print("  推荐使用ORCID进行精确查询，返回的数据包含期刊、文章类型、通讯作者等完整元数据。")
    print("  输出统一附带排名，便于验证排序及后续问题推理。\n")

    for researcher in config["researchers"]:
        orcid = researcher["orcid"]
        name = researcher.get("name", orcid)

        print(f"\n{'=' * 70}")
        print(f"测试研究者: {name} (ORCID: {orcid})")
        print(f"{'=' * 70}")

        publications, api_info, base_question = fetcher.fetch_by_orcid_with_metadata(
            orcid=orcid,
            max_results=config["max_results"],
        )

        total_count = len(publications)
        print(f"[基础问题] 列出所有出版物 → 共 {total_count} 篇")

        index_map = {id(pub): idx for idx, pub in enumerate(publications)}
        formatted_publications = [_format_publication(pub, index_map) for pub in publications]

        for pub in formatted_publications[:3]:
            journal = pub.get("journal") or "Unknown Journal"
            print(
                f"  - #{pub['rank']}: [{pub.get('year', 'N/A')}] "
                f"{(pub.get('title') or '')[:70]}... ({journal})"
            )

        base_result = create_test_result(
            identifier=orcid,
            question=base_question,
            api_info=api_info,
            data=formatted_publications,
            data_key="publications",
            orcid=orcid,
            researcher=name,
        )
        base_result["metadata_available"] = True
        base_result["notes"] = "每条记录附带PMID、期刊、文章类型、DOI和作者角色信息。"

        # ==================== 增强问题 1：通讯作者 ====================
        print(f"\n[增强问题 1/3] 列出作为通讯作者的所有出版物")
        corresponding_pubs = fetcher.filter_by_author_role(publications, "corresponding")
        corresponding_formatted = [_format_publication(pub, index_map) for pub in corresponding_pubs]
        corresponding_percentage = (
            len(corresponding_pubs) / total_count * 100 if total_count else 0
        )

        print(f"  ✓ 找到 {len(corresponding_pubs)} 篇（占比: {corresponding_percentage:.1f}%）")
        for pub in corresponding_formatted[:3]:
            authors = [a.get("name") for a in pub.get("authors", [])[:5]]
            print(
                f"    - #{pub['rank']}: [{pub.get('year', 'N/A')}] "
                f"{(pub.get('title') or '')[:60]}..."
            )
            print(f"      作者: {', '.join(authors)}")

        enhanced_result_1 = {
            "question": f"列出PubMed中{name} (ORCID: {orcid})作为通讯作者的所有出版物",
            "filter_type": "author_role",
            "filter_value": "corresponding",
            "total_count": len(corresponding_pubs),
            "percentage": f"{corresponding_percentage:.1f}%",
            "publications": corresponding_formatted,
        }

        # ==================== 增强问题 2：Review类型 ====================
        print(f"\n[增强问题 2/3] 列出所有Review类型的文章")
        review_pubs = fetcher.filter_by_article_type(publications, "Review")
        review_formatted = [_format_publication(pub, index_map) for pub in review_pubs]
        review_percentage = len(review_pubs) / total_count * 100 if total_count else 0

        print(f"  ✓ 找到 {len(review_pubs)} 篇（占比: {review_percentage:.1f}%）")
        for pub in review_formatted[:3]:
            types = ", ".join(pub.get("article_types", []))
            print(
                f"    - #{pub['rank']}: [{pub.get('year', 'N/A')}] "
                f"{(pub.get('title') or '')[:70]}..."
            )
            print(f"      类型: {types}")

        enhanced_result_2 = {
            "question": f"列出PubMed中{name} (ORCID: {orcid})发表的所有Review类型文章",
            "filter_type": "article_type",
            "filter_value": "Review",
            "total_count": len(review_pubs),
            "percentage": f"{review_percentage:.1f}%",
            "publications": review_formatted,
        }

        # ==================== 增强问题 3：特定期刊 ====================
        journal_counts = Counter()
        for pub in publications:
            journal = pub.get("journal")
            if journal:
                journal_counts[journal] += 1

        if journal_counts:
            top_journal = journal_counts.most_common(1)[0][0]
        else:
            top_journal = "Nature"

        print(f"\n[增强问题 3/3] 列出发表在期刊 '{top_journal}' 的所有出版物")
        journal_pubs = fetcher.filter_by_journal(publications, top_journal)
        journal_formatted = [_format_publication(pub, index_map) for pub in journal_pubs]
        journal_percentage = len(journal_pubs) / total_count * 100 if total_count else 0

        print(f"  ✓ 找到 {len(journal_pubs)} 篇（占比: {journal_percentage:.1f}%）")
        for pub in journal_formatted[:3]:
            print(
                f"    - #{pub['rank']}: [{pub.get('year', 'N/A')}] "
                f"{(pub.get('title') or '')[:70]}..."
            )

        year_counts = defaultdict(int)
        for pub in journal_pubs:
            year = pub.get("year")
            if year:
                year_counts[year] += 1

        print("  年份分布:")
        for year in sorted(year_counts.keys(), reverse=True)[:5]:
            print(f"    {year}: {year_counts[year]}篇")

        enhanced_result_3 = {
            "question": f"列出PubMed中{name} (ORCID: {orcid})在期刊'{top_journal}'发表的所有出版物",
            "filter_type": "journal",
            "filter_value": top_journal,
            "total_count": len(journal_pubs),
            "percentage": f"{journal_percentage:.1f}%",
            "year_distribution": dict(year_counts),
            "publications": journal_formatted,
        }

        researcher_result = {
            "researcher": name,
            "orcid": orcid,
            "base_test": base_result,
            "enhanced_tests": [
                enhanced_result_1,
                enhanced_result_2,
                enhanced_result_3,
            ],
            "api_info": api_info,
            "summary": {
                "total_publications": total_count,
                "as_corresponding_author": len(corresponding_pubs),
                "review_articles": len(review_pubs),
                "in_top_journal": len(journal_pubs),
                "top_journal": top_journal,
            },
        }

        all_results.append(researcher_result)

        if config.get("sleep_seconds"):
            time.sleep(config["sleep_seconds"])

    save_result(
        "academic_research/pubmed",
        {
            "api_name": "PubMed",
            "description": "结合基础枚举与元数据过滤的综合测试，用于评估AI对医学文献的精确枚举能力。",
            "requires_auth": False,
            "rate_limit_note": "默认遵守3 req/sec限制，若提供API Key可提升。",
            "config": config,
            "tests": all_results,
        },
    )

    print(f"\n{'=' * 70}")
    print("✓ PubMed测试完成 (基础 + 元数据增强)")
    print(f"{'=' * 70}\n")

    return all_results


if __name__ == "__main__":
    run()
