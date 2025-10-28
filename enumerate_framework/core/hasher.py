"""Hash计算模块"""

import hashlib


def compute_hash(text: str, length: int = 8) -> str:
    """
    计算文本的SHA256哈希值前N位

    Args:
        text: 要计算hash的文本
        length: 返回hash的长度（默认8位）

    Returns:
        Hash字符串前N位
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:length]
