#!/usr/bin/env python3
"""
主程序 - 生成所有测试数据
"""

import time
from core import TestGenerator
from fetchers import (
    NPMFetcher, PyPIFetcher, GitHubFetcher, DockerFetcher,
    CratesFetcher, RubyGemsFetcher, NuGetFetcher, GoProxyFetcher,
    ArxivFetcher, CondaFetcher
)


def main():
    print("=" * 80)
    print("AI列举能力测试框架 - 数据生成")
    print("=" * 80)

    generator = TestGenerator()

    # NPM包
    print("\n📦 NPM Packages...")
    npm = NPMFetcher()
    for pkg in ['express', 'react']:
        items, api_info, question = npm.fetch(pkg)
        if items:
            generator.add_test_case(
                domain=npm.get_domain_name(pkg),
                question=question,
                items=items,
                api_info=api_info,
                metadata=npm.get_metadata(pkg)
            )
            print(f"  ✓ {pkg}: {len(items)} 个版本")
        time.sleep(1)

    # PyPI包
    print("\n🐍 PyPI Packages...")
    pypi = PyPIFetcher()
    for pkg in ['requests', 'numpy', 'flask']:
        items, api_info, question = pypi.fetch(pkg)
        if items:
            generator.add_test_case(
                domain=pypi.get_domain_name(pkg),
                question=question,
                items=items,
                api_info=api_info,
                metadata=pypi.get_metadata(pkg)
            )
            print(f"  ✓ {pkg}: {len(items)} 个版本")

    # GitHub
    print("\n🐙 GitHub...")
    gh = GitHubFetcher()

    # torvalds的仓库
    items, api_info, question = gh.fetch_repos('torvalds', 50)
    if items:
        generator.add_test_case(
            domain='github_torvalds_repos',
            question=question,
            items=items,
            api_info=api_info,
            metadata={'username': 'torvalds'}
        )
        print(f"  ✓ torvalds repos: {len(items)} 个")
    time.sleep(1)

    # kubernetes的releases
    items, api_info, question = gh.fetch_releases('kubernetes/kubernetes', 100)
    if items:
        generator.add_test_case(
            domain='github_k8s_releases',
            question=question,
            items=items,
            api_info=api_info,
            metadata={'repo': 'kubernetes/kubernetes'}
        )
        print(f"  ✓ k8s releases: {len(items)} 个")
    time.sleep(1)

    # react的branches
    items, api_info, question = gh.fetch_branches('facebook/react', 100)
    if items:
        generator.add_test_case(
            domain='github_react_branches',
            question=question,
            items=items,
            api_info=api_info,
            metadata={'repo': 'facebook/react'}
        )
        print(f"  ✓ react branches: {len(items)} 个")
    time.sleep(1)

    # Docker镜像
    print("\n🐳 Docker Images...")
    docker = DockerFetcher()
    for img in ['python', 'node']:
        items, api_info, question = docker.fetch(img, 100)
        if items:
            generator.add_test_case(
                domain=docker.get_domain_name(img),
                question=question,
                items=items,
                api_info=api_info,
                metadata=docker.get_metadata(img)
            )
            print(f"  ✓ {img}: {len(items)} 个tags")
        time.sleep(1)

    # Rust Crates
    print("\n🦀 Rust Crates...")
    crates = CratesFetcher()
    for pkg in ['serde', 'tokio']:
        items, api_info, question = crates.fetch(pkg)
        if items:
            generator.add_test_case(
                domain=crates.get_domain_name(pkg),
                question=question,
                items=items,
                api_info=api_info,
                metadata=crates.get_metadata(pkg)
            )
            print(f"  ✓ {pkg}: {len(items)} 个版本")
        time.sleep(1)

    # Ruby Gems
    print("\n💎 Ruby Gems...")
    gems = RubyGemsFetcher()
    items, api_info, question = gems.fetch('rails')
    if items:
        generator.add_test_case(
            domain=gems.get_domain_name('rails'),
            question=question,
            items=items,
            api_info=api_info,
            metadata=gems.get_metadata('rails')
        )
        print(f"  ✓ rails: {len(items)} 个版本")
    time.sleep(1)

    # NuGet
    print("\n📘 NuGet Packages...")
    nuget = NuGetFetcher()
    for pkg in ['Newtonsoft.Json', 'EntityFramework']:
        items, api_info, question = nuget.fetch(pkg)
        if items:
            generator.add_test_case(
                domain=nuget.get_domain_name(pkg),
                question=question,
                items=items,
                api_info=api_info,
                metadata=nuget.get_metadata(pkg)
            )
            print(f"  ✓ {pkg}: {len(items)} 个版本")

    # Go
    print("\n🐹 Go Modules...")
    go = GoProxyFetcher()
    for mod in ['github.com/gin-gonic/gin', 'github.com/spf13/cobra']:
        items, api_info, question = go.fetch(mod)
        if items:
            generator.add_test_case(
                domain=go.get_domain_name(mod),
                question=question,
                items=items,
                api_info=api_info,
                metadata=go.get_metadata(mod)
            )
            print(f"  ✓ {mod.split('/')[-1]}: {len(items)} 个版本")

    # arXiv
    print("\n📚 arXiv Papers...")
    arxiv = ArxivFetcher()
    for author in ['LeCun', 'Hinton']:
        items, api_info, question = arxiv.fetch(author, 50)
        if items:
            generator.add_test_case(
                domain=arxiv.get_domain_name(author),
                question=question,
                items=items,
                api_info=api_info,
                metadata=arxiv.get_metadata(author)
            )
            print(f"  ✓ {author}: {len(items)} 篇论文")
        time.sleep(3)  # arXiv建议间隔

    # Conda
    print("\n🐍 Conda Packages...")
    conda = CondaFetcher()
    items, api_info, question = conda.fetch('pandas', 'conda-forge')
    if items:
        generator.add_test_case(
            domain=conda.get_domain_name('pandas'),
            question=question,
            items=items,
            api_info=api_info,
            metadata=conda.get_metadata('pandas', 'conda-forge')
        )
        print(f"  ✓ pandas: {len(items)} 个版本")

    # 保存结果
    print("\n" + "=" * 80)
    output_path = "output/test_cases.json"
    generator.save(output_path)
    stats = generator.get_stats()

    print(f"✓ 已保存到: {output_path}")
    print(f"\n统计:")
    print(f"  测试域: {stats['domains']}")
    print(f"  项目数: {stats['total_items']:,}")
    print(f"  稀疏问题: {stats['total_sparse']}")
    print("=" * 80)


if __name__ == '__main__':
    main()
