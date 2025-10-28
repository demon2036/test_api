"""Spotify API 测试"""

import os
import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, print_header
else:
    from .utils import save_result, print_header


def run(test_config=None):
    """运行Spotify API测试

    Args:
        test_config: 测试配置字典，可包含:
            - artists: 要测试的艺术家列表（格式：[{"id": "...", "name": "..."}, ...]）
            - max_albums: 每个艺术家最多获取多少专辑
    """
    print_header("测试 Spotify API")

    # 检查环境变量
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    if not (client_id and client_secret):
        print("\n⚠️  跳过Spotify测试 - 缺少API凭据")
        print("   请在.env文件中设置SPOTIFY_CLIENT_ID和SPOTIFY_CLIENT_SECRET")
        print("   获取方式: https://developer.spotify.com/dashboard")
        return []

    from fetchers.spotify import SpotifyFetcher
    fetcher = SpotifyFetcher()

    # 默认配置
    config = {
        "artists": [
            {"id": "06HL4z0CvFAxyc27GXpf02", "name": "Taylor Swift"},
            {"id": "3TVXtAsR1Inumwj472S9r4", "name": "Drake"}
        ],
        "max_albums": 200
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    for artist_info in config["artists"]:
        artist_id = artist_info["id"]
        artist_name = artist_info.get("name", artist_id)

        print(f"\n测试艺术家: {artist_name} ({artist_id})")

        try:
            albums, api_info, question = fetcher.fetch_albums(
                artist_id,
                max_albums=config["max_albums"]
            )

            result = {
                "artist_id": artist_id,
                "artist_name": artist_name,
                "question": question,
                "api_info": api_info,
                "total_albums": len(albums),
                "sample_albums": albums[:10] if len(albums) > 10 else albums
            }
            results.append(result)

            print(f"  ✓ 找到 {len(albums)} 张专辑/单曲")
            if len(albums) > 0:
                print(f"  前5张: {albums[:5]}")

        except Exception as e:
            print(f"  ✗ 测试失败: {e}")

    if results:
        save_result("spotify", {
            "api_name": "Spotify",
            "requires_auth": True,
            "auth_type": "OAuth 2.0",
            "config": config,
            "tests": results
        })

    return results


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    run()
