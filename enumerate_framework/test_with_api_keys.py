#!/usr/bin/env python3
"""测试需要API Key的服务"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ 已加载.env文件")
except ImportError:
    print("⚠️  python-dotenv未安装")
    print("   安装方法: pip install python-dotenv")
    sys.exit(1)

# 创建输出目录
OUTPUT_DIR = Path("output/api_tests")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_result(api_name, result_data):
    """保存测试结果到JSON文件"""
    output_file = OUTPUT_DIR / f"{api_name}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 结果已保存: {output_file}")


def check_env_var(var_name):
    """检查环境变量是否设置"""
    value = os.getenv(var_name)
    if value:
        print(f"  ✓ {var_name}: {'*' * 10} (已设置)")
        return True
    else:
        print(f"  ✗ {var_name}: 未设置")
        return False


def test_spotify():
    """测试Spotify API"""
    print("\n" + "="*80)
    print("测试 Spotify API")
    print("="*80)

    # 检查环境变量
    has_client_id = check_env_var('SPOTIFY_CLIENT_ID')
    has_client_secret = check_env_var('SPOTIFY_CLIENT_SECRET')

    if not (has_client_id and has_client_secret):
        print("\n⚠️  跳过Spotify测试 - 缺少API凭据")
        print("   请在.env文件中设置SPOTIFY_CLIENT_ID和SPOTIFY_CLIENT_SECRET")
        print("   获取方式: https://developer.spotify.com/dashboard")
        return

    from fetchers.spotify import SpotifyFetcher

    try:
        fetcher = SpotifyFetcher()

        # Taylor Swift: spotify:artist:06HL4z0CvFAxyc27GXpf02
        artist_id = "06HL4z0CvFAxyc27GXpf02"
        print(f"\n测试艺术家: {artist_id} (Taylor Swift)")

        albums, api_info, question = fetcher.fetch_albums(artist_id, max_albums=50)

        result = {
            "artist_id": artist_id,
            "question": question,
            "api_info": api_info,
            "total_albums": len(albums),
            "sample_albums": albums[:10] if len(albums) > 10 else albums,
            "timestamp": datetime.now().isoformat()
        }

        print(f"  ✓ 找到 {len(albums)} 张专辑/单曲")
        print(f"  前5张: {albums[:5]}")

        save_result("spotify", {
            "api_name": "Spotify",
            "requires_auth": True,
            "auth_type": "OAuth 2.0",
            "tests": [result]
        })

    except Exception as e:
        print(f"  ✗ Spotify测试失败: {e}")


def test_youtube():
    """测试YouTube API"""
    print("\n" + "="*80)
    print("测试 YouTube API")
    print("="*80)

    # 检查环境变量
    has_api_key = check_env_var('YOUTUBE_API_KEY')

    if not has_api_key:
        print("\n⚠️  跳过YouTube测试 - 缺少API Key")
        print("   请在.env文件中设置YOUTUBE_API_KEY")
        print("   获取方式: https://console.cloud.google.com/apis/credentials")
        return

    from fetchers.youtube import YouTubeFetcher

    try:
        fetcher = YouTubeFetcher()

        # 3Blue1Brown channel
        channel_id = "UCYO_jab_esuFRV4b17AJtAw"
        print(f"\n测试频道: {channel_id} (3Blue1Brown)")

        videos, api_info, question = fetcher.fetch_videos(channel_id, max_videos=50)

        result = {
            "channel_id": channel_id,
            "question": question,
            "api_info": api_info,
            "total_videos": len(videos),
            "sample_videos": videos[:10] if len(videos) > 10 else videos,
            "timestamp": datetime.now().isoformat()
        }

        print(f"  ✓ 找到 {len(videos)} 个视频")
        print(f"  前3个: {videos[:3]}")

        save_result("youtube", {
            "api_name": "YouTube",
            "requires_auth": True,
            "auth_type": "API Key",
            "tests": [result]
        })

    except Exception as e:
        print(f"  ✗ YouTube测试失败: {e}")


def test_tmdb():
    """测试TMDb API"""
    print("\n" + "="*80)
    print("测试 TMDb API")
    print("="*80)

    # 检查环境变量
    has_api_key = check_env_var('TMDB_API_KEY')

    if not has_api_key:
        print("\n⚠️  跳过TMDb测试 - 缺少API Key")
        print("   请在.env文件中设置TMDB_API_KEY")
        print("   获取方式: https://www.themoviedb.org/settings/api")
        return

    from fetchers.tmdb import TMDbFetcher

    try:
        fetcher = TMDbFetcher()

        # Tom Hanks: person_id=31
        person_id = 31
        print(f"\n测试演员: person_id={person_id} (Tom Hanks)")

        credits, api_info, question = fetcher.fetch_person_credits(person_id)

        result = {
            "person_id": person_id,
            "question": question,
            "api_info": api_info,
            "total_credits": len(credits),
            "sample_credits": credits[:10] if len(credits) > 10 else credits,
            "timestamp": datetime.now().isoformat()
        }

        print(f"  ✓ 找到 {len(credits)} 部作品")
        print(f"  前3部: {credits[:3]}")

        save_result("tmdb", {
            "api_name": "TMDb",
            "requires_auth": True,
            "auth_type": "API Key",
            "tests": [result]
        })

    except Exception as e:
        print(f"  ✗ TMDb测试失败: {e}")


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("需要API Key的服务测试")
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
        test_spotify()
        test_youtube()
        test_tmdb()

        print("\n" + "="*80)
        print("✓ 测试完成!")
        print("="*80)
        print(f"\n结果已保存到: {OUTPUT_DIR.absolute()}")

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
