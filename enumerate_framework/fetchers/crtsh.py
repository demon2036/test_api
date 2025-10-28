"""crt.sh Certificate Transparency Log Fetcher"""

import requests
from typing import List, Dict, Tuple
from .base import BaseFetcher


class CrtShFetcher(BaseFetcher):
    """crt.sh证书透明度日志获取器 - 查询域名的所有SSL证书"""

    def fetch_domain_certificates(self, domain: str, max_certs: int = 10000) -> Tuple[List[str], Dict, str]:
        """获取域名的所有SSL/TLS证书"""
        api_url = "https://crt.sh/"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"q": f"%.{domain}", "output": "json"},
            "authentication": "None",
            "rate_limit": "No official limit (be respectful)",
            "documentation": "https://crt.sh/"
        }

        try:
            params = {
                "q": f"%.{domain}",
                "output": "json"
            }

            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()

                certificates = []
                seen = set()

                for cert in data:
                    name_value = cert.get('name_value', '')
                    issuer_name = cert.get('issuer_name', 'Unknown')
                    not_before = cert.get('not_before', 'Unknown')
                    not_after = cert.get('not_after', 'Unknown')

                    # Handle multiple domains in one cert
                    for subdomain in name_value.split('\n'):
                        subdomain = subdomain.strip()
                        if subdomain and subdomain not in seen:
                            cert_info = f"{subdomain} (Valid: {not_before[:10]} to {not_after[:10]})"
                            certificates.append(cert_info)
                            seen.add(subdomain)

                            if len(certificates) >= max_certs:
                                break

                    if len(certificates) >= max_certs:
                        break

                question = f"列出crt.sh中域名{domain}的所有SSL/TLS证书和子域名"
                return certificates[:max_certs], api_info, question

        except Exception as e:
            print(f"  ✗ crt.sh API错误 ({domain}): {e}")

        return [], api_info, ""

    # 实现抽象方法
    def fetch(self, **kwargs) -> Tuple[List[str], Dict, str]:
        domain = kwargs.get('domain')
        if domain:
            return self.fetch_domain_certificates(domain)
        return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        return f"crtsh_{kwargs.get('domain', 'unknown').replace('.', '_')}"

    def get_metadata(self, **kwargs) -> Dict:
        return {
            "domain": kwargs.get('domain'),
            "platform": "crt.sh"
        }
