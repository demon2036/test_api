"DBLP API 增强测试 - 元数据过滤"

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from ..utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行DBLP API增强测试

    测试结构：
    - 1个基础问题：列出所有出版物
    - 3个增强问题：
      1. 第2作者的论文（元数据：作者位置）
      2. CVPR会议论文（元数据：会议名称）
      3. 2020年后论文（元数据：发表年份）
    """
    print_header("测试 DBLP API - 基础 + 元数据增强")

    from fetchers.academic_research.dblp import DBLPFetcher
    fetcher = DBLPFetcher()

    # 默认配置
    config = {
        "authors": [
            {"pid": "l/YannLeCun", "name": "Yann LeCun"},
        ],
        "max_publications": 10000
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    all_results = []

    for author in config["authors"]:
        pid = author["pid"]
        name = author["name"]

        print(f"\n{'='*70}")
        print(f"测试作者: {name} (PID: {pid})")
        print(f"{ '='*70}")

        # ==================== 基础问题 ====================
        print(f"\n[基础问题] 列出所有出版物")
        pubs_with_metadata, api_info, base_question = fetcher.fetch_with_metadata(
            pid=pid,
            max_publications=config["max_publications"]
        )

        total_count = len(pubs_with_metadata)
        print(f"  ✓ 找到 {total_count} 篇出版物")
        print(f"  前3篇:")
        for pub in pubs_with_metadata[:3]:
            print(f"    - [{pub['year']}] {pub['title'][:80]}...")

        # 保存基础结果
        base_result = {
            "question": base_question,
            "total_count": total_count,
            "publications": [
                {
                    "title": p['title'],
                    "year": p['year'],
                    "type": p['type'],
                    "venue": p['venue']
                } for p in pubs_with_metadata
            ],
            "metadata_available": True
        }

        # ==================== 增强问题 1：第2作者 ====================
        print(f"\n[增强问题 1/3] 列出作为第2作者的所有出版物")
        print(f"  说明: 这需要知道每篇论文的完整作者列表和作者顺序")

        second_author_pubs = fetcher.filter_by_author_position(pubs_with_metadata, 2)

        filtered_count = len(second_author_pubs)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 篇（占比: {percentage:.1f}%）")
        print(f"  前3篇:")
        for pub in second_author_pubs[:3]:
            authors_str = ", ".join(pub['authors'][:3])
            if len(pub['authors']) > 3:
                authors_str += ", ..."
            print(f"    - [{pub['year']}] {pub['title'][:60]}...")
            print(f"      作者: {authors_str}")

        enhanced_result_1 = {
            "question": f"列出DBLP中作者{name} (PID: {pid})作为第2作者的所有出版物",
            "filter_type": "author_position",
            "filter_value": 2,
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "publications": [
                {
                    "title": p['title'],
                    "authors": p['authors'],
                    "year": p['year'],
                    "venue": p['venue']
                } for p in second_author_pubs
            ]
        }

        # ==================== 增强问题 2：CVPR会议 ====================
        print(f"\n[增强问题 2/3] 列出发表在CVPR会议的所有出版物")
        print(f"  说明: 这需要知道每篇论文的会议/期刊名称")

        cvpr_pubs = fetcher.filter_by_venue(pubs_with_metadata, "CVPR")

        filtered_count = len(cvpr_pubs)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 篇（占比: {percentage:.1f}%）")
        print(f"  前3篇:")
        for pub in cvpr_pubs[:3]:
            print(f"    - [{pub['year']}] {pub['title'][:70]}...")
            print(f"      会议: {pub['venue']}")

        enhanced_result_2 = {
            "question": f"列出DBLP中作者{name} (PID: {pid})发表在CVPR会议的所有出版物",
            "filter_type": "venue",
            "filter_value": "CVPR",
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "publications": [
                {
                    "title": p['title'],
                    "year": p['year'],
                    "venue": p['venue'],
                    "authors": p['authors'][:3]  # 只保留前3位作者
                } for p in cvpr_pubs
            ]
        }

        # ==================== 增强问题 3：2020年后 ====================
        print(f"\n[增强问题 3/3] 列出2020年后发表的所有出版物")
        print(f"  说明: 这需要知道每篇论文的发表年份")

        recent_pubs = fetcher.filter_by_year(pubs_with_metadata, min_year=2020)

        filtered_count = len(recent_pubs)
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0

        print(f"  ✓ 找到 {filtered_count} 篇（占比: {percentage:.1f}%）")
        print(f"  前3篇:")
        for pub in recent_pubs[:3]:
            print(f"    - [{pub['year']}] {pub['title'][:70]}...")

        # 按年份分组统计
        from collections import defaultdict
        year_counts = defaultdict(int)
        for pub in recent_pubs:
            if pub['year']:
                year_counts[pub['year']] += 1

        print(f"  年份分布:")
        for year in sorted(year_counts.keys(), reverse=True):
            print(f"    {year}: {year_counts[year]}篇")

        enhanced_result_3 = {
            "question": f"列出DBLP中作者{name} (PID: {pid})在2020年后发表的所有出版物",
            "filter_type": "year",
            "filter_value": {"min_year": 2020},
            "total_count": filtered_count,
            "percentage": f"{percentage:.1f}%",
            "year_distribution": dict(year_counts),
            "publications": [
                {
                    "title": p['title'],
                    "year": p['year'],
                    "type": p['type'],
                    "venue": p['venue']
                } for p in recent_pubs
            ]
        }

        # ==================== 汇总结果 ====================
        author_result = {
            "author": name,
            "pid": pid,
            "base_test": base_result,
            "enhanced_tests": [
                enhanced_result_1,
                enhanced_result_2,
                enhanced_result_3
            ],
            "api_info": api_info,
            "summary": {
                "total_publications": total_count,
                "as_2nd_author": len(second_author_pubs),
                "at_cvpr": len(cvpr_pubs),
                "since_2020": len(recent_pubs)
            }
        }

        all_results.append(author_result)

    # 保存结果
    save_result("academic_research/dblp_enhanced", {
        "api_name": "DBLP (Enhanced with Metadata Filtering)",
        "description": "测试AI的深度枚举能力：不仅要列举所有项目，还要根据元数据过滤",
        "requires_auth": False,
        "difficulty_level": "Advanced (Level 2)",
        "config": config,
        "tests": all_results
    })

    print(f"\n{'='*70}")
    print(f"✓ DBLP增强测试完成!")
    print(f"{ '='*70}")
    print(f"\n测试难度提升：")
    print(f"  Level 1 (基础): 列举所有出版物")
    print(f"  Level 2 (增强): 列举并过滤 - 需要理解每篇论文的详细元数据")
    print(f"\n结果已保存: output/api_tests/academic_research/dblp_enhanced.json")

    return all_results


if __name__ == "__main__":
    run()
