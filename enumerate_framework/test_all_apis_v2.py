#!/usr/bin/env python3
"""模块化的API测试运行器 - 无需认证的API"""

import sys
from pathlib import Path

# 加载环境变量（可选）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv未安装（可选）")

# 导入所有无需认证的测试模块
from test_runners import (
    test_npm,
    test_pypi,
    test_github,
    test_docker,
    test_crates,
    test_cran,      # 新增：R packages
    test_homebrew,  # 新增：macOS/Linux packages
    test_dblp,      # 替换arXiv
    test_crtsh,
    test_openlibrary,
    test_sec_edgar,
    test_pubmed,
    test_zenodo     # 新增：Research data
)


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("模块化API测试 - 无需认证的API")
    print("="*80)

    output_dir = Path("output/api_tests")
    print(f"\n输出目录: {output_dir.absolute()}")

    print("\n将测试以下无需认证的API:")
    print("  1. NPM Registry")
    print("  2. PyPI")
    print("  3. GitHub")
    print("  4. Docker Hub")
    print("  5. Crates.io")
    print("  6. CRAN (R packages)")
    print("  7. Homebrew (macOS/Linux packages)")
    print("  8. DBLP (计算机科学论文 - 使用精确PID)")
    print("  9. crt.sh (SSL证书)")
    print("  10. Open Library")
    print("  11. SEC EDGAR (美国公司文件)")
    print("  12. PubMed (支持ORCID)")
    print("  13. Zenodo (研究数据)")

    print("\n开始测试...\n")

    try:
        # 运行所有测试
        test_npm.run()
        test_pypi.run()
        test_github.run()
        test_docker.run()
        test_crates.run()
        test_cran.run()       # 新增：R packages
        test_homebrew.run()   # 新增：macOS/Linux packages
        test_dblp.run()       # 使用PID精确查询，替换arXiv
        test_crtsh.run()
        test_openlibrary.run()
        test_sec_edgar.run()
        test_pubmed.run()     # 支持ORCID
        test_zenodo.run()     # 新增：研究数据

        print("\n" + "="*80)
        print("✓ 所有测试完成!")
        print("="*80)
        print(f"\n所有结果已保存到: {output_dir.absolute()}")

        print("\n查看结果:")
        print(f"  ls {output_dir}")
        for json_file in sorted(output_dir.glob("*.json")):
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
