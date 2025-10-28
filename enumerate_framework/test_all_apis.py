#!/usr/bin/env python3
"""完整的API测试脚本 - 为每个API生成独立的输出文件"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# 创建输出目录
OUTPUT_DIR = Path("output/api_tests")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 加载环境变量（如果有）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv未安装，将跳过需要API key的测试")
    print("   安装方法: pip install python-dotenv")


def save_result(api_name, result_data):
    """保存测试结果到JSON文件"""
    output_file = OUTPUT_DIR / f"{api_name}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 结果已保存: {output_file}")


def test_npm():
    """测试NPM API"""
    print("\n" + "="*80)
    print("测试 NPM Registry API")
    print("="*80)

    from fetchers.npm import NPMFetcher
    fetcher = NPMFetcher()

    test_packages = ['react', 'vue', 'express']
    results = []

    for pkg in test_packages:
        print(f"\n测试包: {pkg}")
        versions, api_info, question = fetcher.fetch(package=pkg)

        result = {
            "package": pkg,
            "question": question,
            "api_info": api_info,
            "total_versions": len(versions),
            "sample_versions": versions[:10] if len(versions) > 10 else versions,
            "all_versions": versions,
            "timestamp": datetime.now().isoformat()
        }
        results.append(result)

        print(f"  ✓ 找到 {len(versions)} 个版本")
        print(f"  前5个版本: {versions[:5]}")

    save_result("npm", {
        "api_name": "NPM Registry",
        "requires_auth": False,
        "tests": results
    })


def test_pypi():
    """测试PyPI API"""
    print("\n" + "="*80)
    print("测试 PyPI API")
    print("="*80)

    from fetchers.pypi import PyPIFetcher
    fetcher = PyPIFetcher()

    test_packages = ['requests', 'numpy', 'django']
    results = []

    for pkg in test_packages:
        print(f"\n测试包: {pkg}")
        versions, api_info, question = fetcher.fetch(package=pkg)

        result = {
            "package": pkg,
            "question": question,
            "api_info": api_info,
            "total_versions": len(versions),
            "sample_versions": versions[:10] if len(versions) > 10 else versions,
            "all_versions": versions,
            "timestamp": datetime.now().isoformat()
        }
        results.append(result)

        print(f"  ✓ 找到 {len(versions)} 个版本")
        print(f"  前5个版本: {versions[:5]}")

    save_result("pypi", {
        "api_name": "PyPI",
        "requires_auth": False,
        "tests": results
    })


def test_github():
    """测试GitHub API"""
    print("\n" + "="*80)
    print("测试 GitHub API")
    print("="*80)

    from fetchers.github import GitHubFetcher
    fetcher = GitHubFetcher()

    results = []

    # Test repos
    print("\n测试用户仓库: torvalds")
    repos, api_info, question = fetcher.fetch_repos('torvalds', max_repos=50)
    results.append({
        "type": "repos",
        "username": "torvalds",
        "question": question,
        "api_info": api_info,
        "total_repos": len(repos),
        "repos": repos,
        "timestamp": datetime.now().isoformat()
    })
    print(f"  ✓ 找到 {len(repos)} 个仓库")

    time.sleep(1)

    # Test tags
    print("\n测试仓库标签: torvalds/linux")
    tags, api_info, question = fetcher.fetch_tags('torvalds/linux', max_tags=50)
    results.append({
        "type": "tags",
        "repo": "torvalds/linux",
        "question": question,
        "api_info": api_info,
        "total_tags": len(tags),
        "sample_tags": tags[:10],
        "timestamp": datetime.now().isoformat()
    })
    print(f"  ✓ 找到 {len(tags)} 个标签")

    save_result("github", {
        "api_name": "GitHub",
        "requires_auth": False,
        "note": "未认证速率限制: 60 req/hour",
        "tests": results
    })


def test_docker():
    """测试Docker Hub API"""
    print("\n" + "="*80)
    print("测试 Docker Hub API")
    print("="*80)

    from fetchers.docker import DockerFetcher
    fetcher = DockerFetcher()

    test_images = ['python', 'node', 'nginx']
    results = []

    for img in test_images:
        print(f"\n测试镜像: {img}")
        tags, api_info, question = fetcher.fetch(image=img, limit=100)

        result = {
            "image": img,
            "question": question,
            "api_info": api_info,
            "total_tags": len(tags),
            "sample_tags": tags[:10] if len(tags) > 10 else tags,
            "timestamp": datetime.now().isoformat()
        }
        results.append(result)

        print(f"  ✓ 找到 {len(tags)} 个标签")
        print(f"  前5个标签: {tags[:5]}")

    save_result("docker", {
        "api_name": "Docker Hub",
        "requires_auth": False,
        "tests": results
    })


def test_crates():
    """测试Crates.io API"""
    print("\n" + "="*80)
    print("测试 Crates.io API")
    print("="*80)

    from fetchers.crates import CratesFetcher
    fetcher = CratesFetcher()

    test_crates = ['serde', 'tokio', 'regex']
    results = []

    for crate in test_crates:
        print(f"\n测试crate: {crate}")
        versions, api_info, question = fetcher.fetch(crate=crate)

        result = {
            "crate": crate,
            "question": question,
            "api_info": api_info,
            "total_versions": len(versions),
            "sample_versions": versions[:10] if len(versions) > 10 else versions,
            "timestamp": datetime.now().isoformat()
        }
        results.append(result)

        print(f"  ✓ 找到 {len(versions)} 个版本")
        time.sleep(1)  # Respect rate limit

    save_result("crates", {
        "api_name": "Crates.io",
        "requires_auth": False,
        "tests": results
    })


def test_arxiv():
    """测试arXiv API"""
    print("\n" + "="*80)
    print("测试 arXiv API")
    print("="*80)

    from fetchers.arxiv import ArxivFetcher
    fetcher = ArxivFetcher()

    test_authors = ['Yann LeCun', 'Yoshua Bengio']
    results = []

    for author in test_authors:
        print(f"\n测试作者: {author}")
        papers, api_info, question = fetcher.fetch(author=author, max_results=50)

        result = {
            "author": author,
            "question": question,
            "api_info": api_info,
            "total_papers": len(papers),
            "sample_papers": papers[:5] if len(papers) > 5 else papers,
            "timestamp": datetime.now().isoformat()
        }
        results.append(result)

        print(f"  ✓ 找到 {len(papers)} 篇论文")
        time.sleep(3)  # Respect rate limit

    save_result("arxiv", {
        "api_name": "arXiv",
        "requires_auth": False,
        "tests": results
    })


def test_crtsh():
    """测试crt.sh API"""
    print("\n" + "="*80)
    print("测试 crt.sh 证书透明度 API")
    print("="*80)

    from fetchers.crtsh import CrtShFetcher
    fetcher = CrtShFetcher()

    test_domains = ['github.com', 'google.com']
    results = []

    for domain in test_domains:
        print(f"\n测试域名: {domain}")
        certs, api_info, question = fetcher.fetch(domain=domain, max_certs=100)

        result = {
            "domain": domain,
            "question": question,
            "api_info": api_info,
            "total_certificates": len(certs),
            "sample_certificates": certs[:10] if len(certs) > 10 else certs,
            "timestamp": datetime.now().isoformat()
        }
        results.append(result)

        print(f"  ✓ 找到 {len(certs)} 个证书/子域名")
        print(f"  前5个: {certs[:5]}")

    save_result("crtsh", {
        "api_name": "crt.sh",
        "requires_auth": False,
        "tests": results
    })


def test_openlibrary():
    """测试Open Library API"""
    print("\n" + "="*80)
    print("测试 Open Library API")
    print("="*80)

    from fetchers.goodreads import OpenLibraryFetcher
    fetcher = OpenLibraryFetcher()

    # Isaac Asimov
    author_key = "OL34221A"
    print(f"\n测试作者: {author_key} (Isaac Asimov)")
    works, api_info, question = fetcher.fetch_author_works(author_key, max_works=50)

    result = {
        "author_key": author_key,
        "question": question,
        "api_info": api_info,
        "total_works": len(works),
        "sample_works": works[:10] if len(works) > 10 else works,
        "timestamp": datetime.now().isoformat()
    }

    print(f"  ✓ 找到 {len(works)} 部作品")
    print(f"  前5部: {works[:5]}")

    save_result("openlibrary", {
        "api_name": "Open Library",
        "requires_auth": False,
        "tests": [result]
    })


def test_sec_edgar():
    """测试SEC EDGAR API"""
    print("\n" + "="*80)
    print("测试 SEC EDGAR API")
    print("="*80)

    from fetchers.sec_edgar import SECEdgarFetcher
    fetcher = SECEdgarFetcher()

    # Apple Inc.
    cik = "320193"
    print(f"\n测试公司: CIK {cik} (Apple Inc.)")
    filings, api_info, question = fetcher.fetch_company_filings(cik, max_filings=50)

    result = {
        "cik": cik,
        "question": question,
        "api_info": api_info,
        "total_filings": len(filings),
        "sample_filings": filings[:10] if len(filings) > 10 else filings,
        "timestamp": datetime.now().isoformat()
    }

    print(f"  ✓ 找到 {len(filings)} 个文件提交")
    print(f"  最近5个: {filings[:5]}")

    save_result("sec_edgar", {
        "api_name": "SEC EDGAR",
        "requires_auth": False,
        "tests": [result]
    })


def test_pubmed():
    """测试PubMed API"""
    print("\n" + "="*80)
    print("测试 PubMed API")
    print("="*80)

    from fetchers.pubmed import PubMedFetcher
    fetcher = PubMedFetcher()

    author = "Fauci AS"
    print(f"\n测试作者: {author}")
    print("  注意: PubMed有速率限制，测试可能较慢...")
    pubs, api_info, question = fetcher.fetch_author_publications(author, max_results=20)

    result = {
        "author": author,
        "question": question,
        "api_info": api_info,
        "total_publications": len(pubs),
        "sample_publications": pubs[:10] if len(pubs) > 10 else pubs,
        "timestamp": datetime.now().isoformat()
    }

    print(f"  ✓ 找到 {len(pubs)} 篇论文")
    print(f"  前3篇: {pubs[:3]}")

    save_result("pubmed", {
        "api_name": "PubMed",
        "requires_auth": False,
        "note": "速率限制: 3 req/sec",
        "tests": [result]
    })


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("完整API测试 - 为每个API生成独立输出文件")
    print("="*80)
    print(f"\n输出目录: {OUTPUT_DIR.absolute()}")
    print("\n将测试以下无需认证的API:")
    print("  1. NPM Registry")
    print("  2. PyPI")
    print("  3. GitHub")
    print("  4. Docker Hub")
    print("  5. Crates.io")
    print("  6. arXiv")
    print("  7. crt.sh")
    print("  8. Open Library")
    print("  9. SEC EDGAR")
    print("  10. PubMed")
    print("\n开始测试...\n")

    try:
        test_npm()
        test_pypi()
        test_github()
        test_docker()
        test_crates()
        test_arxiv()
        test_crtsh()
        test_openlibrary()
        test_sec_edgar()
        test_pubmed()

        print("\n" + "="*80)
        print("✓ 所有测试完成!")
        print("="*80)
        print(f"\n所有结果已保存到: {OUTPUT_DIR.absolute()}")
        print("\n查看结果:")
        print(f"  ls {OUTPUT_DIR}")
        for json_file in sorted(OUTPUT_DIR.glob("*.json")):
            print(f"    - {json_file.name}")

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
