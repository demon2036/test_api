"""Spotify API测试 - 完整枚举，无截断，充分利用metadata"""

import os
import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, print_header
else:
    from ..utils import save_result, print_header


def run(test_config=None):
    """运行Spotify API测试 - 展示真正的Enumerate All能力"""
    print_header("测试 Spotify API - 完整枚举")

    # 检查环境变量
    if not (os.getenv('SPOTIFY_CLIENT_ID') and os.getenv('SPOTIFY_CLIENT_SECRET')):
        print("\n⚠️  跳过Spotify测试 - 缺少API凭据")
        print("   请在.env文件中设置SPOTIFY_CLIENT_ID和SPOTIFY_CLIENT_SECRET")
        print("   获取方式: https://developer.spotify.com/dashboard")
        return []

    from fetchers.media_entertainment.spotify import SpotifyFetcher
    fetcher = SpotifyFetcher()

    # 默认测试艺术家
    config = {
        "artists": [
            {"id": "2c32JruIkUyfdycHmhIph4", "name": "花譜 (KAF)"},
        ]
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    for artist_info in config["artists"]:
        artist_id = artist_info["id"]
        artist_name = artist_info.get("name", artist_id)

        print(f"\n{'='*60}")
        print(f"测试艺术家: {artist_name} ({artist_id})")
        print(f"{'='*60}")

        try:
            # ============================================
            # 1. 获取所有专辑（完整metadata）
            # ============================================
            albums, api_info, question = fetcher.fetch_albums(artist_id)

            result = {
                "artist_id": artist_id,
                "artist_name": artist_name,
                "api_info": api_info,
                "tests": []
            }

            print(f"\n[1] 基础枚举: {question}")
            print(f"  ✓ 总计: {len(albums)} 张专辑/单曲")
            print(f"\n  完整列表:")
            for i, album in enumerate(albums, 1):
                print(f"    {i}. {fetcher.format_album(album)}")

            result["tests"].append({
                "question": question,
                "total": len(albums),
                "all_items": [fetcher.format_album(a) for a in albums]
            })

            # ============================================
            # 2. 高级查询 - 合作专辑
            # ============================================
            collab_albums = fetcher.filter_collaboration_albums(albums)
            collab_question = f"列出Spotify艺术家 {artist_name} 的所有合作专辑"

            print(f"\n[2] 高级查询: {collab_question}")
            print(f"  ✓ 总计: {len(collab_albums)} 张")
            if collab_albums:
                print(f"  完整列表:")
                for i, album in enumerate(collab_albums, 1):
                    print(f"    {i}. {fetcher.format_album(album)}")
            else:
                print(f"  (无合作专辑)")

            result["tests"].append({
                "question": collab_question,
                "total": len(collab_albums),
                "all_items": [fetcher.format_album(a) for a in collab_albums]
            })

            # ============================================
            # 3. 高级查询 - 按年份筛选完整专辑
            # ============================================
            # 首先分离出完整专辑和单曲
            only_albums = fetcher.filter_albums_by_type(albums, "album")
            only_singles = fetcher.filter_albums_by_type(albums, "single")

            # 在完整专辑上应用年份过滤器
            year_albums = fetcher.filter_albums_by_year(only_albums, year_start=2020)
            year_question = f"列出Spotify艺术家 {artist_name} 在2020年及之后发行的完整专辑"

            print(f"\n[3] 高级查询: {year_question}")
            print(f"  ✓ 总计: {len(year_albums)} 张")
            if year_albums:
                print(f"  完整列表:")
                for i, album in enumerate(year_albums, 1):
                    print(f"    {i}. {fetcher.format_album(album)}")

            result["tests"].append({
                "question": year_question,
                "total": len(year_albums),
                "all_items": [fetcher.format_album(a) for a in year_albums]
            })

            # ============================================
            # 4. 高级查询 - 按类型筛选
            # ============================================
            album_question = f"列出Spotify艺术家 {artist_name} 的所有完整专辑（不含单曲）"
            single_question = f"列出Spotify艺术家 {artist_name} 的所有单曲"

            print(f"\n[4a] 高级查询: {album_question}")
            print(f"  ✓ 总计: {len(only_albums)} 张")
            if only_albums:
                print(f"  完整列表:")
                for i, album in enumerate(only_albums, 1):
                    print(f"    {i}. {fetcher.format_album(album)}")

            print(f"\n[4b] 高级查询: {single_question}")
            print(f"  ✓ 总计: {len(only_singles)} 张")
            if only_singles:
                print(f"  完整列表:")
                for i, single in enumerate(only_singles, 1):
                    print(f"    {i}. {fetcher.format_album(single)}")

            result["tests"].append({
                "question": album_question,
                "total": len(only_albums),
                "all_items": [fetcher.format_album(a) for a in only_albums]
            })

            result["tests"].append({
                "question": single_question,
                "total": len(only_singles),
                "all_items": [fetcher.format_album(a) for a in only_singles]
            })

            # ============================================
            # 5. 曲目级别查询（如果有专辑）
            # ============================================
            if albums:
                # 选择专辑《寓話γ》进行测试，如果找不到则使用第一张专辑
                test_album = next((a for a in albums if a['name'] == '寓話γ'), None)
                if not test_album:
                    print("  (专项测试警告: 未在列表中找到专辑《寓話γ》。将使用找到的第一张专辑进行后续曲目测试。)")
                    test_album = next((a for a in albums if a.get('album_type') == 'album'), albums[0])
                album_id = test_album['id']
                album_name = test_album['name']

                print(f"\n[5] 曲目枚举: 列出专辑《{album_name}》的所有曲目")

                tracks, _, _ = fetcher.fetch_tracks(album_id)
                print(f"  ✓ 总计: {len(tracks)} 首曲目")
                print(f"  完整列表:")
                for track in tracks:
                    print(f"    {fetcher.format_track(track)}")

                # 筛选长曲目（>5分钟）
                long_tracks = fetcher.filter_tracks_by_duration(tracks, min_ms=300000)
                print(f"\n[5b] 高级查询: 筛选长曲目（>5分钟）")
                print(f"  ✓ 总计: {len(long_tracks)} 首")
                if long_tracks:
                    for track in long_tracks:
                        print(f"    {fetcher.format_track(track)}")

                result["tests"].append({
                    "question": f"列出专辑《{album_name}》的所有曲目",
                    "total": len(tracks),
                    "all_items": [fetcher.format_track(t) for t in tracks]
                })

                result["tests"].append({
                    "question": f"列出专辑《{album_name}》中时长超过5分钟的曲目",
                    "total": len(long_tracks),
                    "all_items": [fetcher.format_track(t) for t in long_tracks]
                })

            results.append(result)

        except Exception as e:
            print(f"  ✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()

    # 保存完整结果（无截断）
    if results:
        save_result("media_entertainment/spotify", {
            "api_name": "Spotify",
            "requires_auth": True,
            "auth_type": "OAuth 2.0",
            "philosophy": "Enumerate All - Complete enumeration without truncation",
            "metadata_utilized": [
                "artists (collaboration filtering)",
                "release_date (year filtering)",
                "album_type (album/single separation)",
                "duration_ms (length filtering)"
            ],
            "config": config,
            "results": results
        })

    print(f"\n{'='*60}")
    print(f"✓ Spotify测试完成 - 所有结果已完整枚举并保存")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    run()
