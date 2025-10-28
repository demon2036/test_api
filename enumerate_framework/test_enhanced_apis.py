#!/usr/bin/env python3
"""元数据增强测试运行器 - 测试AI的深度枚举能力

这个脚本运行增强版的API测试，每个测试包含：
- 1个基础问题：列出所有X
- 2-3个增强问题：列出所有X，其中满足元数据条件Y

目前支持的API：
1. DBLP - 计算机科学论文（作者位置、会议/期刊、年份）
2. GitHub - 代码仓库（star数、编程语言、创建日期）
3. Spotify - 音乐专辑（需API Key）
4. PubMed - 生物医学论文（需实现）

难度提升：
- Level 1（基础）：简单枚举所有项目
- Level 2（增强）：枚举 + 元数据过滤 - 需要理解每个项目的详细信息
"""

import sys
from pathlib import Path

# 导入增强测试模块
from test_runners import (
    test_dblp_enhanced,
    test_github_enhanced,
    test_npm_enhanced,
    test_pypi_enhanced,
    test_github_forked_repos,
    # test_spotify_enhanced,  # 需要API Key
    # test_pubmed_enhanced,   # TODO: 待实现
)


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("元数据增强测试 - 测试AI的深度枚举能力")
    print("="*80)

    output_dir = Path("output/api_tests")
    print(f"\n输出目录: {output_dir.absolute()}")

    print("\n测试模式:")
    print("  ✓ Level 1 (基础): 列举所有项目")
    print("  ✓ Level 2 (增强): 列举 + 元数据过滤")

    print("\n将测试以下API（增强模式）:")
    print("  1. DBLP - 计算机科学论文")
    print("     • 基础: 列出所有论文")
    print("     • 增强: 第2作者论文、CVPR论文、2020年后论文")
    print("\n  2. GitHub - 代码仓库")
    print("     • 基础: 列出所有仓库")
    print("     • 增强: Star>1000、C语言、2010年后创建")
    print("\n  3. GitHub Forked Repos - 代码仓库")
    print("     • 基础: 列出所有forked仓库")
    print("     • 增强: (目前无，待添加)")
    print("\n  4. NPM - JavaScript包")
    print("     • 基础: 列出所有版本")
    print("     • 增强: 2024年发布、Major版本、被废弃的版本")
    print("\n  5. PyPI - Python包")
    print("     • 基础: 列出所有版本")
    print("     • 增强: 2024年发布、包含wheel、被撤回的版本")

    print("\n开始测试...\n")

    try:
        # 运行DBLP增强测试
        print("\n" + "="*80)
        test_dblp_enhanced.run()

        # 运行GitHub增强测试
        print("\n" + "="*80)
        test_github_enhanced.run()

        # 运行GitHub Forked Repos测试
        print("\n" + "="*80)
        test_github_forked_repos.run()

        # 运行NPM增强测试
        print("\n" + "="*80)
        test_npm_enhanced.run()

        # 运行PyPI增强测试
        print("\n" + "="*80)
        test_pypi_enhanced.run()

        print("\n" + "="*80)
        print("✓ 所有增强测试完成!")
        print("="*80)
        print(f"\n所有结果已保存到: {output_dir.absolute()}")

        print("\n查看增强测试结果:")
        print(f"  ls {output_dir}")
        for json_file in sorted(output_dir.glob("*_enhanced.json")):
            print(f"    - {json_file.name}")

        print("\n增强测试的价值:")
        print("  1. 测试更深层的理解能力 - 不仅要列举，还要理解每个项目的详细信息")
        print("  2. 测试过滤能力 - 能否根据元数据准确过滤")
        print("  3. 测试完整性 - 是否真的获取了所有项目的元数据")
        print("  4. 更接近真实使用场景 - 如\"列出我作为第一作者的所有论文\"")

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
