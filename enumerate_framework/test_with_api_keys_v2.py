#!/usr/bin/env python3
"""模块化的API测试运行器 - 需要API Key的服务"""

import os
import sys

# 加载.env文件
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ 已加载.env文件")
except ImportError:
    print("⚠️  python-dotenv未安装")
    print("   安装方法: pip install python-dotenv")
    sys.exit(1)

# 导入需要认证的测试模块
from test_runners import test_spotify, test_youtube, test_tmdb


def check_env_var(var_name):
    """检查环境变量是否设置"""
    value = os.getenv(var_name)
    if value:
        print(f"  ✓ {var_name}: {'*' * 10} (已设置)")
        return True
    else:
        print(f"  ✗ {var_name}: 未设置")
        return False


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("模块化API测试 - 需要API Key的服务")
    print("="*80)

    print("\n本脚本测试以下需要API Key的服务:")
    print("  1. Spotify (需要CLIENT_ID和CLIENT_SECRET)")
    print("  2. YouTube (需要API_KEY)")
    print("  3. TMDb (需要API_KEY)")

    print("\n请确保已在.env文件中配置相应的API凭据")
    print("\n检查环境变量...")

    # 检查所有环境变量
    print("\n" + "-"*80)
    env_status = {
        "Spotify": {
            "SPOTIFY_CLIENT_ID": check_env_var('SPOTIFY_CLIENT_ID'),
            "SPOTIFY_CLIENT_SECRET": check_env_var('SPOTIFY_CLIENT_SECRET')
        },
        "YouTube": {
            "YOUTUBE_API_KEY": check_env_var('YOUTUBE_API_KEY')
        },
        "TMDb": {
            "TMDB_API_KEY": check_env_var('TMDB_API_KEY')
        }
    }

    # 统计
    total_vars = sum(len(vars) for vars in env_status.values())
    configured_vars = sum(sum(vars.values()) for vars in env_status.values())

    print("\n" + "-"*80)
    print(f"环境变量配置状态: {configured_vars}/{total_vars}")

    if configured_vars == 0:
        print("\n⚠️  未配置任何API凭据！")
        print("\n请按照以下步骤配置:")
        print("  1. 复制 .env.example 为 .env")
        print("     cp .env.example .env")
        print("\n  2. 编辑 .env 文件，填入你的API凭据")
        print("\n  3. 重新运行此脚本")
        sys.exit(1)

    print("\n开始测试...\n")

    try:
        # 运行所有已配置的测试
        test_spotify.run()
        test_youtube.run()
        test_tmdb.run()

        print("\n" + "="*80)
        print("✓ 测试完成!")
        print("="*80)

        from pathlib import Path
        output_dir = Path("output/api_tests")
        print(f"\n结果已保存到: {output_dir.absolute()}")

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
