"""SEC EDGAR API Fetcher (美国证券交易委员会)"""

import requests
from typing import List, Dict, Tuple
from .base import BaseFetcher


class SECEdgarFetcher(BaseFetcher):
    """SEC EDGAR公司文件获取器"""

    def fetch_company_filings(self, cik: str, max_filings: int = 1000) -> Tuple[List[str], Dict, str]:
        """
        获取公司的所有SEC文件提交
        CIK: Central Index Key (公司唯一标识符)
        """
        # Pad CIK to 10 digits
        cik_padded = cik.zfill(10)
        api_url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {},
            "authentication": "None (User-Agent required)",
            "rate_limit": "10 requests/second",
            "documentation": "https://www.sec.gov/edgar/sec-api-documentation"
        }

        try:
            # SEC requires User-Agent header
            headers = {
                "User-Agent": "Research Project research@example.com"
            }

            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                filings_data = data.get('filings', {}).get('recent', {})

                if not filings_data:
                    return [], api_info, ""

                # Extract filing information
                accession_numbers = filings_data.get('accessionNumber', [])
                filing_dates = filings_data.get('filingDate', [])
                forms = filings_data.get('form', [])
                primary_docs = filings_data.get('primaryDocument', [])

                filings = []
                for i in range(min(len(accession_numbers), max_filings)):
                    filing_info = f"{forms[i]} - {filing_dates[i]} - {accession_numbers[i]}"
                    filings.append(filing_info)

                company_name = data.get('name', f'CIK {cik}')
                question = f"列出SEC公司{company_name} (CIK: {cik})的所有文件提交"
                return filings, api_info, question

        except Exception as e:
            print(f"  ✗ SEC EDGAR API错误 (CIK {cik}): {e}")

        return [], api_info, ""

    def fetch_form_type(self, cik: str, form_type: str, max_filings: int = 500) -> Tuple[List[str], Dict, str]:
        """获取公司特定类型的所有文件 (例如: 10-K, 10-Q, 8-K)"""
        cik_padded = cik.zfill(10)
        api_url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"

        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"filter_form": form_type},
            "authentication": "None (User-Agent required)",
            "rate_limit": "10 requests/second",
            "documentation": "https://www.sec.gov/edgar/sec-api-documentation"
        }

        try:
            headers = {
                "User-Agent": "Research Project research@example.com"
            }

            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                filings_data = data.get('filings', {}).get('recent', {})

                if not filings_data:
                    return [], api_info, ""

                accession_numbers = filings_data.get('accessionNumber', [])
                filing_dates = filings_data.get('filingDate', [])
                forms = filings_data.get('form', [])

                # Filter by form type
                filtered_filings = []
                for i in range(len(forms)):
                    if forms[i] == form_type and len(filtered_filings) < max_filings:
                        filing_info = f"{forms[i]} - {filing_dates[i]} - {accession_numbers[i]}"
                        filtered_filings.append(filing_info)

                company_name = data.get('name', f'CIK {cik}')
                question = f"列出SEC公司{company_name} (CIK: {cik})的所有{form_type}文件"
                return filtered_filings, api_info, question

        except Exception as e:
            print(f"  ✗ SEC EDGAR API错误 (CIK {cik}, Form {form_type}): {e}")

        return [], api_info, ""

    # 实现抽象方法
    def fetch(self, **kwargs) -> Tuple[List[str], Dict, str]:
        cik = kwargs.get('cik')
        form_type = kwargs.get('form_type')
        if cik and form_type:
            return self.fetch_form_type(cik, form_type)
        elif cik:
            return self.fetch_company_filings(cik)
        return [], {}, ""

    def get_domain_name(self, **kwargs) -> str:
        cik = kwargs.get('cik', 'unknown')
        form_type = kwargs.get('form_type')
        if form_type:
            return f"sec_edgar_cik_{cik}_{form_type}"
        return f"sec_edgar_cik_{cik}"

    def get_metadata(self, **kwargs) -> Dict:
        return {
            "cik": kwargs.get('cik'),
            "form_type": kwargs.get('form_type'),
            "platform": "SEC EDGAR"
        }
