"""API Fetcher基类"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple


class BaseFetcher(ABC):
    """所有API fetcher的基类"""

    @abstractmethod
    def fetch(self, **kwargs) -> Tuple[List[str], Dict, str]:
        """
        获取数据

        Returns:
            Tuple[items, api_info, question]
            - items: 项目列表
            - api_info: API调用信息字典
            - question: 列举问题描述
        """
        pass

    @abstractmethod
    def get_domain_name(self, **kwargs) -> str:
        """获取域名称"""
        pass

    @abstractmethod
    def get_metadata(self, **kwargs) -> Dict:
        """获取元数据"""
        pass
