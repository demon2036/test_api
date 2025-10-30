"""DBLP 测试运行器的工具函数模块

这个模块包含所有可复用的函数，用于简化代码并实现参数复用。
"""

from collections import defaultdict
from ..utils import create_test_result


# ============= 数据处理函数 =============

def create_index_map(publications):
    """创建出版物的索引映射，用于排名"""
    return {id(pub): idx for idx, pub in enumerate(publications)}


def calculate_percentage(filtered_count, total_count):
    """计算过滤结果的百分比"""
    return (filtered_count / total_count * 100) if total_count else 0


def format_publication(pub, index_map):
    """为输出添加排序信息和核心元数据"""
    idx = index_map.get(id(pub), -1)
    return {
        "rank": idx + 1 if idx >= 0 else None,
        "answer": pub.get("title"),
        "year": pub.get("year"),
        "venue": pub.get("venue"),
        "type": pub.get("type"),
        "authors": pub.get("authors", []),
        "author_position": pub.get("author_position"),
        "ee": pub.get("ee"),
    }


def format_publications_list(publications, index_map):
    """批量格式化出版物列表"""
    return [format_publication(pub, index_map) for pub in publications]


# ============= 显示函数 =============

def print_section_header(title, width=70):
    """打印带分隔线的章节标题"""
    print(f"\n{'=' * width}")
    print(title)
    print(f"{'=' * width}")


def print_preview(formatted_pubs, max_items=3, show_authors=False):
    """打印出版物预览（前N条）

    Args:
        formatted_pubs: 格式化后的出版物列表
        max_items: 最多显示条数
        show_authors: 是否显示作者信息
    """
    for pub in formatted_pubs[:max_items]:
        year = pub.get('year', 'N/A')
        answer = (pub.get('answer') or '')[:70]
        print(f"  - #{pub['rank']}: [{year}] {answer}...")

        if show_authors and pub.get('authors'):
            authors = pub['authors']
            authors_preview = ", ".join(authors[:3])
            if len(authors) > 3:
                authors_preview += ", ..."
            print(f"    作者: {authors_preview}")


def print_filter_stats(filtered_count, total_count, label="✓ 找到"):
    """打印过滤统计信息"""
    percentage = calculate_percentage(filtered_count, total_count)
    print(f"  {label} {filtered_count} 篇（占比: {percentage:.1f}%）")


def print_year_distribution(publications, indent="  "):
    """打印年份分布统计"""
    year_counts = defaultdict(int)
    for pub in publications:
        if pub.get("year"):
            year_counts[pub["year"]] += 1

    if year_counts:
        print(f"{indent}年份分布:")
        for year in sorted(year_counts.keys(), reverse=True):
            print(f"{indent}  {year}: {year_counts[year]}篇")

    return dict(year_counts)


# ============= 结果构建函数 =============

def build_enhanced_result(question, filter_type, filter_value,
                         filtered_pubs, total_count, index_map,
                         extra_data=None):
    """构建增强测试结果

    Args:
        question: 问题描述
        filter_type: 过滤类型（保留用于兼容性，不输出到结果）
        filter_value: 过滤值（保留用于兼容性，不输出到结果）
        filtered_pubs: 过滤后的出版物列表（原始数据）
        total_count: 总数（保留用于兼容性，不输出到结果）
        index_map: 索引映射
        extra_data: 额外数据（如年份分布，保留用于兼容性，不输出到结果）

    Returns:
        增强测试结果字典（包含 question, answers, answer_count）
    """
    formatted_pubs = format_publications_list(filtered_pubs, index_map)

    # 使用 create_test_result 自动添加 answer_count 和 timestamp
    result = create_test_result(
        question=question,
        answers=formatted_pubs
    )

    return result


def build_author_result(author_name, pid, base_result, enhanced_results,
                       api_info, summary_dict):
    """构建作者测试结果

    Args:
        author_name: 作者名称
        pid: PID标识符
        base_result: 基础测试结果
        enhanced_results: 增强测试结果列表
        api_info: API信息
        summary_dict: 摘要统计

    Returns:
        作者测试结果字典
    """
    return {
        "author": author_name,
        "pid": pid,
        "base_test": base_result,
        "enhanced_tests": enhanced_results,
        "api_info": api_info,
        "summary": summary_dict,
    }


# ============= 增强问题执行函数 =============

def run_enhanced_question(fetcher, publications, index_map, total_count,
                         filter_func, filter_args, question_template,
                         author_name, pid, question_num, total_questions,
                         show_preview_func=None, extra_stats_func=None):
    """运行单个增强问题的通用函数

    Args:
        fetcher: DBLP fetcher实例
        publications: 原始出版物列表
        index_map: 索引映射
        total_count: 总数
        filter_func: 过滤函数（如 fetcher.filter_by_author_position）
        filter_args: 过滤函数参数（字典）
        question_template: 问题模板
        author_name: 作者名称
        pid: PID标识符
        question_num: 问题编号
        total_questions: 总问题数
        show_preview_func: 自定义预览显示函数
        extra_stats_func: 额外统计函数（如年份分布）

    Returns:
        增强测试结果字典
    """
    # 打印问题标题
    print(f"\n[增强问题 {question_num}/{total_questions}] {question_template['display']}")

    # 执行过滤
    filtered_pubs = filter_func(publications, **filter_args)

    # 打印统计
    print_filter_stats(len(filtered_pubs), total_count)

    # 打印预览
    if show_preview_func:
        show_preview_func(filtered_pubs, index_map)
    else:
        formatted = format_publications_list(filtered_pubs, index_map)
        print_preview(formatted, max_items=3)

    # 计算额外统计
    extra_data = {}
    if extra_stats_func:
        extra_data = extra_stats_func(filtered_pubs)

    # 构建结果
    full_question = question_template['full'].format(
        author_name=author_name,
        pid=pid
    )

    return build_enhanced_result(
        question=full_question,
        filter_type=question_template['filter_type'],
        filter_value=question_template['filter_value'],
        filtered_pubs=filtered_pubs,
        total_count=total_count,
        index_map=index_map,
        extra_data=extra_data
    )
