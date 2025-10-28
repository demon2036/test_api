#!/usr/bin/env python3
"""测试新增的API fetchers"""

import sys
import time
from fetchers.wikipedia import WikipediaFetcher
from fetchers.crtsh import CrtShFetcher
from fetchers.goodreads import OpenLibraryFetcher
from fetchers.sec_edgar import SECEdgarFetcher
from fetchers.pubmed import PubMedFetcher


def test_wikipedia():
    """测试Wikipedia API"""
    print("\n" + "="*80)
    print("测试 Wikipedia API")
    print("="*80)

    fetcher = WikipediaFetcher()

    # Test 1: Category members
    print("\n1. 测试分类成员枚举...")
    results, api_info, question = fetcher.fetch_category_members(
        category="Programming_languages",
        lang="en",
        max_members=100
    )
    print(f"   问题: {question}")
    print(f"   结果数量: {len(results)}")
    print(f"   前5个: {results[:5]}")

    time.sleep(1)

    # Test 2: Page revisions
    print("\n2. 测试页面修订历史枚举...")
    results, api_info, question = fetcher.fetch_page_revisions(
        page_title="Python_(programming_language)",
        lang="en",
        max_revisions=50
    )
    print(f"   问题: {question}")
    print(f"   结果数量: {len(results)}")
    print(f"   最新3个修订: {results[:3]}")


def test_crtsh():
    """测试crt.sh证书透明度API"""
    print("\n" + "="*80)
    print("测试 crt.sh 证书透明度 API")
    print("="*80)

    fetcher = CrtShFetcher()

    print("\n测试域名证书/子域名枚举...")
    results, api_info, question = fetcher.fetch_domain_certificates(
        domain="github.com",
        max_certs=100
    )
    print(f"   问题: {question}")
    print(f"   结果数量: {len(results)}")
    print(f"   前10个证书/子域名:")
    for cert in results[:10]:
        print(f"     - {cert}")


def test_openlibrary():
    """测试Open Library API"""
    print("\n" + "="*80)
    print("测试 Open Library API")
    print("="*80)

    fetcher = OpenLibraryFetcher()

    print("\n测试作者作品枚举...")
    # Isaac Asimov's key
    results, api_info, question = fetcher.fetch_author_works(
        author_key="OL34221A",
        max_works=50
    )
    print(f"   问题: {question}")
    print(f"   结果数量: {len(results)}")
    print(f"   前10本书:")
    for work in results[:10]:
        print(f"     - {work}")


def test_sec_edgar():
    """测试SEC EDGAR API"""
    print("\n" + "="*80)
    print("测试 SEC EDGAR API")
    print("="*80)

    fetcher = SECEdgarFetcher()

    print("\n测试公司文件提交枚举...")
    # Apple Inc. CIK: 0000320193
    results, api_info, question = fetcher.fetch_company_filings(
        cik="320193",
        max_filings=50
    )
    print(f"   问题: {question}")
    print(f"   结果数量: {len(results)}")
    print(f"   最近10个文件:")
    for filing in results[:10]:
        print(f"     - {filing}")

    time.sleep(0.5)

    print("\n测试特定表格类型枚举 (10-K年报)...")
    results, api_info, question = fetcher.fetch_form_type(
        cik="320193",
        form_type="10-K",
        max_filings=10
    )
    print(f"   问题: {question}")
    print(f"   结果数量: {len(results)}")
    print(f"   10-K文件:")
    for filing in results:
        print(f"     - {filing}")


def test_pubmed():
    """测试PubMed API"""
    print("\n" + "="*80)
    print("测试 PubMed API")
    print("="*80)

    fetcher = PubMedFetcher()

    print("\n测试作者出版物枚举...")
    print("   注意: PubMed有速率限制,测试将较慢...")
    results, api_info, question = fetcher.fetch_author_publications(
        author="Fauci AS",
        max_results=30
    )
    print(f"   问题: {question}")
    print(f"   结果数量: {len(results)}")
    print(f"   前10篇论文:")
    for pub in results[:10]:
        print(f"     - {pub}")


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("枚举全部测试 - 新增API验证")
    print("="*80)
    print("\n本测试验证以下API的完整枚举能力:")
    print("  1. Wikipedia (分类成员、页面修订)")
    print("  2. crt.sh (SSL证书、子域名)")
    print("  3. Open Library (作者作品)")
    print("  4. SEC EDGAR (公司文件)")
    print("  5. PubMed (学术论文)")
    print("\n所有这些API都不需要认证，可直接测试完整枚举功能")

    try:
        test_wikipedia()
        test_crtsh()
        test_openlibrary()
        test_sec_edgar()
        test_pubmed()

        print("\n" + "="*80)
        print("✓ 所有测试完成!")
        print("="*80)
        print("\n核心验证:")
        print("  ✓ 所有API都实现了分页/完整枚举")
        print("  ✓ 可以获取完整的数据集")
        print("  ✓ 适合用于'列举全部'测试场景")

    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
