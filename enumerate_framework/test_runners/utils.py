"""测试运行器的通用工具函数"""

import json
from datetime import datetime
from pathlib import Path

# 脚本文件所在目录 - 使用resolve()获取绝对路径
BASE_DIR = Path(__file__).resolve().parent.parent
# 定位到 enumerate_framework/output/api_tests
OUTPUT_DIR = BASE_DIR / "output" / "api_tests"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_result(api_name, result_data):
    """保存测试结果到JSON文件

    Args:
        api_name: API名称（用作文件名,可以包含子目录）
        result_data: 要保存的数据字典
    """
    output_file = OUTPUT_DIR / f"{api_name}.json"
    # 确保父目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 结果已保存: {output_file}")


def create_test_result(question, answers, api_info=None, **extra_fields):
    """创建标准格式的测试结果

    Args:
        question: 问题描述
        answers: 答案列表（可以是简单值列表或包含元数据的字典列表）
        api_info: API信息字典（可选）
        **extra_fields: 其他要包含的字段

    Returns:
        dict: 格式化的测试结果
    """
    # Ensure answers is at least an empty list to simplify downstream handling
    normalized_answers = answers if isinstance(answers, list) else [answers] if answers is not None else []

    result = {
        "question": question,
        "answers": normalized_answers,
        "answer_count": len(normalized_answers),
        "timestamp": datetime.now().isoformat()
    }

    # 如果提供了api_info，则添加
    if api_info:
        result["api_info"] = api_info

    # 添加额外字段
    result.update(extra_fields)

    return result


def print_header(title):
    """打印格式化的标题"""
    print("\n" + "="*80)
    print(title)
    print("="*80)
