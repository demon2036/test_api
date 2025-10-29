"""Homebrew Formulae API Fetcher"""

import requests
from typing import List, Dict, Tuple
from ..base import BaseFetcher


class HomebrewFetcher(BaseFetcher):
    """Homebrew formula版本获取器"""

    def fetch(self, formula: str) -> Tuple[List[str], Dict, str]:
        """获取Homebrew formula的所有版本

        Args:
            formula: Formula名称 (e.g., "python", "node")
        """
        api_url = f"https://formulae.brew.sh/api/formula/{formula}.json"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://formulae.brew.sh/docs/api/"
        }

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()

                # Get current version
                current_version = data.get('versions', {}).get('stable', 'Unknown')

                # Homebrew API primarily tracks current version, not historical versions
                # But we can get bottle versions (platform-specific builds)
                versions = [current_version]

                # Get versioned formula variants if available
                versioned_formulae = data.get('versioned_formulae', [])
                if versioned_formulae:
                    versions.extend(versioned_formulae)

                question = f"列出Homebrew上{formula}的当前版本和变体"
                return versions, api_info, question

            elif response.status_code == 404:
                print(f"  ✗ Homebrew formula '{formula}' 不存在")
        except Exception as e:
            print(f"  ✗ Homebrew API错误 ({formula}): {e}")

        return [], api_info, ""

    def fetch_with_metadata(self, formula: str) -> Tuple[Dict, Dict, str]:
        """获取Homebrew formula的详细信息（含完整元数据）

        返回完整的formula元数据，包括：
        - name: Formula名称
        - desc: 描述
        - versions: 版本信息
        - service: Service配置（如有）
        - keg_only: 是否keg-only
        - keg_only_reason: Keg-only原因
        - aliases: 别名列表
        - dependencies: 依赖列表
        - 其他详细信息
        """
        api_url = f"https://formulae.brew.sh/api/formula/{formula}.json"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://formulae.brew.sh/docs/api/"
        }

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                question = f"列出Homebrew上{formula}的完整信息（含元数据）"
                return data, api_info, question
            elif response.status_code == 404:
                print(f"  ✗ Homebrew formula '{formula}' 不存在")
        except Exception as e:
            print(f"  ✗ Homebrew API错误 ({formula}): {e}")

        return {}, api_info, ""

    def fetch_all_formulae(self, max_formulae: int = 10000) -> Tuple[List[str], Dict, str]:
        """获取所有Homebrew formulae名称（仅名称列表，向后兼容）"""
        api_url = "https://formulae.brew.sh/api/formula.json"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://formulae.brew.sh/docs/api/"
        }

        try:
            response = requests.get(api_url, timeout=15)
            if response.status_code == 200:
                formulae = response.json()
                formula_names = [f.get('name', '') for f in formulae if 'name' in f]
                formula_names = formula_names[:max_formulae]

                question = "列出Homebrew的所有formula名称"
                return formula_names, api_info, question
        except Exception as e:
            print(f"  ✗ Homebrew API错误: {e}")

        return [], api_info, ""

    def fetch_all_formulae_with_metadata(self, max_formulae: int = 10000) -> Tuple[List[Dict], Dict, str]:
        """获取所有Homebrew formulae（包含完整元数据）"""
        api_url = "https://formulae.brew.sh/api/formula.json"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None",
            "rate_limit": "No official limit",
            "documentation": "https://formulae.brew.sh/docs/api/"
        }

        try:
            response = requests.get(api_url, timeout=15)
            if response.status_code == 200:
                formulae = response.json()[:max_formulae]
                question = "列出Homebrew的所有formula（含元数据）"
                return formulae, api_info, question
        except Exception as e:
            print(f"  ✗ Homebrew API错误: {e}")

        return [], api_info, ""

    def get_domain_name(self, formula: str) -> str:
        return f"homebrew_{formula.replace('-', '_')}"

    def get_metadata(self, formula: str) -> Dict:
        return {"formula": formula, "ecosystem": "macOS/Linux/Homebrew"}

    def filter_with_service(self, formulae_with_metadata: List[Dict]) -> List[Dict]:
        """过滤有service定义的formulae

        Args:
            formulae_with_metadata: 包含元数据的formula列表

        Returns:
            有service定义的formula列表

        Example:
            # 查找所有可以作为服务运行的formulae
            service_formulae = fetcher.filter_with_service(formulae)
        """
        return [f for f in formulae_with_metadata if f.get('service') is not None]

    def filter_keg_only(self, formulae_with_metadata: List[Dict]) -> List[Dict]:
        """过滤keg-only的formulae

        keg-only的formula不会被链接到系统路径，通常是为了避免与系统版本冲突

        Args:
            formulae_with_metadata: 包含元数据的formula列表

        Returns:
            keg-only的formula列表

        Example:
            # 查找所有keg-only的formulae
            keg_only_formulae = fetcher.filter_keg_only(formulae)
        """
        return [f for f in formulae_with_metadata if f.get('keg_only', False)]

    def filter_with_aliases(self, formulae_with_metadata: List[Dict]) -> List[Dict]:
        """过滤有别名的formulae

        Args:
            formulae_with_metadata: 包含元数据的formula列表

        Returns:
            有别名的formula列表

        Example:
            # 查找所有有别名的formulae
            aliased_formulae = fetcher.filter_with_aliases(formulae)
        """
        return [f for f in formulae_with_metadata if len(f.get('aliases', [])) > 0]

    def filter_deprecated(self, formulae_with_metadata: List[Dict]) -> List[Dict]:
        """过滤已弃用的formulae

        Args:
            formulae_with_metadata: 包含元数据的formula列表

        Returns:
            已弃用的formula列表
        """
        return [f for f in formulae_with_metadata if f.get('deprecated', False)]

    def get_service_info(self, formula_data: Dict) -> Dict:
        """提取formula的service详细信息

        Args:
            formula_data: 单个formula的元数据字典

        Returns:
            Service信息字典，如果没有service则返回None

        Example:
            service_info = fetcher.get_service_info(formula_data)
            if service_info:
                print(f"Service: {service_info['run_command']}")
        """
        service = formula_data.get('service')
        if not service:
            return None

        return {
            'name': formula_data.get('name', ''),
            'run_command': ' '.join(service.get('run', [])),
            'run_type': service.get('run_type', ''),
            'keep_alive': service.get('keep_alive', {}),
            'working_dir': service.get('working_dir', ''),
            'log_path': service.get('log_path', ''),
            'error_log_path': service.get('error_log_path', '')
        }

    def get_keg_only_reason(self, formula_data: Dict) -> Dict:
        """获取formula的keg-only原因

        Args:
            formula_data: 单个formula的元数据字典

        Returns:
            Keg-only原因字典，如果不是keg-only则返回None

        Example:
            reason = fetcher.get_keg_only_reason(formula_data)
            if reason:
                print(f"{reason['name']} is keg-only: {reason['explanation']}")
        """
        if not formula_data.get('keg_only', False):
            return None

        keg_only_reason = formula_data.get('keg_only_reason', {})
        return {
            'name': formula_data.get('name', ''),
            'reason': keg_only_reason.get('reason', ''),
            'explanation': keg_only_reason.get('explanation', '')
        }

    def get_aliases(self, formula_data: Dict) -> Dict:
        """获取formula的别名列表

        Args:
            formula_data: 单个formula的元数据字典

        Returns:
            包含formula名称和别名列表的字典

        Example:
            alias_info = fetcher.get_aliases(formula_data)
            print(f"{alias_info['name']} aliases: {alias_info['aliases']}")
        """
        return {
            'name': formula_data.get('name', ''),
            'aliases': formula_data.get('aliases', [])
        }
