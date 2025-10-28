"""测试运行器的通用工具函数"""

import json
from datetime import datetime
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path("output/api_tests")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_result(api_name, result_data):
    """保存测试结果到JSON文件

    Args:
        api_name: API名称（用作文件名）
        result_data: 要保存的数据字典
    """
    output_file = OUTPUT_DIR / f"{api_name}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 结果已保存: {output_file}")


def create_test_result(identifier, question, api_info, data, data_key, **extra_fields):
    """创建标准格式的测试结果

    Args:
        identifier: 标识符（如package名、author名等）
        question: 问题描述
        api_info: API信息字典
        data: 数据列表
        data_key: 数据在结果中的键名
        **extra_fields: 其他要包含的字段

    Returns:
        dict: 格式化的测试结果
    """
    result = {
        "question": question,
        "api_info": api_info,
        f"total_{data_key}": len(data),
        f"sample_{data_key}": data[:10] if len(data) > 10 else data,
        "timestamp": datetime.now().isoformat()
    }

    # 添加额外字段
    result.update(extra_fields)

    # 如果数据量不太大，包含完整数据
    if len(data) <= 10000:
        result[f"all_{data_key}"] = data

    return result


def print_header(title):
    """打印格式化的标题"""
    print("\n" + "="*80)
    print(title)
    print("="*80)
