"""测试用例生成器"""

import json
from datetime import datetime
from typing import List, Dict, Any
from .hasher import compute_hash


class TestGenerator:
    """生成列举测试用例"""

    def __init__(self):
        self.test_cases = []

    def add_test_case(
        self,
        domain: str,
        question: str,
        items: List[str],
        api_info: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> Dict:
        """
        添加一个测试用例

        Args:
            domain: 测试域名称
            question: 列举问题
            items: 完整的项目列表
            api_info: API调用信息
            metadata: 额外元数据

        Returns:
            生成的测试用例
        """
        # 为每个项目计算hash
        items_with_hash = [
            {"item": item, "hash": compute_hash(item)}
            for item in items
        ]

        # 选择稀疏的hash目标（最多10个）
        step = max(1, len(items_with_hash) // 5)
        sparse_targets = items_with_hash[::step][:10]

        test_case = {
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "api_info": api_info,
            "enumerate_question": {
                "question": question,
                "answer": items,
                "count": len(items)
            },
            "sparse_questions": [
                {
                    "question": f"在{question.replace('列出所有', '')}中，找到SHA256哈希值前8位为 {t['hash']} 的项目。",
                    "hash_prefix": t['hash'],
                    "answer": t['item']
                }
                for t in sparse_targets
            ]
        }

        self.test_cases.append(test_case)
        return test_case

    def save(self, filepath: str):
        """保存测试用例到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.test_cases, f, ensure_ascii=False, indent=2)

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            "domains": len(self.test_cases),
            "total_items": sum(tc['enumerate_question']['count'] for tc in self.test_cases),
            "total_sparse": sum(len(tc['sparse_questions']) for tc in self.test_cases)
        }
