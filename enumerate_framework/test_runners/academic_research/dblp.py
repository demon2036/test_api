# dblp_api_tester.py

import sys
import time
from pathlib import Path



# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
    from test_runners.academic_research.dblp_utils import (
        create_index_map, format_publications_list, print_section_header,
        print_preview, print_filter_stats, print_year_distribution,
        build_enhanced_result, build_author_result
    )
    from test_runners.academic_research.test_config.dblp import config
else:
    from ..utils import save_result, create_test_result, print_header
    from .dblp_utils import (
        create_index_map, format_publications_list, print_section_header,
        print_preview, print_filter_stats, print_year_distribution,
        build_enhanced_result, build_author_result
    )
    from .test_config.dblp import config


def run(test_config=None):
    """运行DBLP API测试，整合基础枚举与元数据过滤能力"""
    print_header("测试 DBLP API (基础 + 元数据增强)")

    from fetchers.academic_research.dblp import DBLPFetcher

    fetcher = DBLPFetcher()

    # 如果传入自定义配置，则覆盖默认配置
    if test_config:
        config.update(test_config)

    results = []

    print("\n说明:")
    print("  DBLP使用PID（永久标识符）确保精确查询，默认完整枚举所有出版物。")
    print("  统一的输出包含排名、作者顺序、会议/期刊等丰富元数据。\n")

    for author_info in config["authors"]:
        pid = author_info["pid"]
        author_name = author_info.get("name", pid)

        # 打印作者标题
        print_section_header(f"测试作者: {author_name} (PID: {pid})")

        # 获取数据
        publications, api_info, question = fetcher.fetch_with_metadata(
            pid=pid,
            max_publications=config["max_publications"],
        )

        total_count = len(publications)
        print(f"[基础问题] 列出所有出版物 → 共 {total_count} 篇")

        # 创建索引映射和格式化
        index_map = create_index_map(publications)
        formatted_publications = format_publications_list(publications, index_map)

        # 打印预览
        print_preview(formatted_publications, max_items=3)

        # 创建基础结果
        base_result = create_test_result(
            question=question,
            answers=formatted_publications,
            api_info=api_info,
            pid=pid,
            author_name=author_name,
            metadata_available=True,
            notes="每条记录包含排名、作者列表、作者顺序、venue和类型等元数据。"
        )

        # ==================== 增强问题 1：第2作者 ====================
        print(f"\n[增强问题 1/3] 列出作为第2作者的所有出版物")
        second_author_pubs = fetcher.filter_by_author_position(publications, 2)
        print_filter_stats(len(second_author_pubs), total_count)

        # 打印预览（带作者信息）
        second_author_formatted = format_publications_list(second_author_pubs, index_map)
        for pub in second_author_formatted[:3]:
            authors_preview = ", ".join(pub["authors"][:3])
            if len(pub["authors"]) > 3:
                authors_preview += ", ..."
            print(f"    - #{pub['rank']}: [{pub.get('year', 'N/A')}] "
                  f"{(pub.get('answer') or '')[:60]}...")
            print(f"      作者: {authors_preview}")

        enhanced_result_1 = build_enhanced_result(
            question=f"列出DBLP中作者{author_name} (PID: {pid})作为第2作者的所有出版物",
            filter_type="author_position",
            filter_value=2,
            filtered_pubs=second_author_pubs,
            total_count=total_count,
            index_map=index_map
        )

        # ==================== 增强问题 2：CVPR会议 ====================
        print(f"\n[增强问题 2/3] 列出发表在CVPR会议的所有出版物")
        cvpr_pubs = fetcher.filter_by_venue(publications, "CVPR")
        print_filter_stats(len(cvpr_pubs), total_count)

        # 打印预览（带会议信息）
        cvpr_formatted = format_publications_list(cvpr_pubs, index_map)
        for pub in cvpr_formatted[:3]:
            print(f"    - #{pub['rank']}: [{pub.get('year', 'N/A')}] "
                  f"{(pub.get('answer') or '')[:70]}...")
            print(f"      会议: {pub.get('venue')}")

        enhanced_result_2 = build_enhanced_result(
            question=f"列出DBLP中作者{author_name} (PID: {pid})发表在CVPR会议的所有出版物",
            filter_type="venue",
            filter_value="CVPR",
            filtered_pubs=cvpr_pubs,
            total_count=total_count,
            index_map=index_map
        )

        # ==================== 增强问题 3：2020年后 ====================
        print(f"\n[增强问题 3/3] 列出2020年后发表的所有出版物")
        recent_pubs = fetcher.filter_by_year(publications, min_year=2020)
        print_filter_stats(len(recent_pubs), total_count)

        # 打印预览
        recent_formatted = format_publications_list(recent_pubs, index_map)
        print_preview(recent_formatted, max_items=3)

        # 打印年份分布
        year_distribution = print_year_distribution(recent_pubs)

        enhanced_result_3 = build_enhanced_result(
            question=f"列出DBLP中作者{author_name} (PID: {pid})在2020年后发表的所有出版物",
            filter_type="year",
            filter_value={"min_year": 2020},
            filtered_pubs=recent_pubs,
            total_count=total_count,
            index_map=index_map,
            extra_data={"year_distribution": year_distribution}
        )

        # 构建作者结果
        author_result = build_author_result(
            author_name=author_name,
            pid=pid,
            base_result=base_result,
            enhanced_results=[
                enhanced_result_1,
                enhanced_result_2,
                enhanced_result_3,
            ],
            api_info=api_info,
            summary_dict={
                "total_publications": total_count,
                "as_2nd_author": len(second_author_pubs),
                "at_cvpr": len(cvpr_pubs),
                "since_2020": len(recent_pubs),
            }
        )

        results.append(author_result)

        # 延时控制
        if config.get("sleep_seconds"):
            time.sleep(config["sleep_seconds"])

    save_result(
        "academic_research/dblp",
        {
            "api_name": "DBLP",
            "description": "基础枚举与元数据过滤相结合，验证AI能否完整列举并理解出版物元数据。",
            "requires_auth": False,
            "identifier_system": "PID (永久标识符)",
            "config": config,
            "tests": results,
        },
    )

    print(f"\n{'=' * 70}")
    print("✓ DBLP测试完成 (基础 + 元数据增强)")
    print(f"{'=' * 70}\n")

    return results


if __name__ == "__main__":
    run()
