"""Spotify API测试 - 完整枚举，无截断，充分利用metadata"""

import sys
from pathlib import Path
from typing import Dict, List

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
    from test_runners.media_entertainment.media_utils import (
        check_spotify_credentials, merge_test_config,
        print_section_header, print_test_info, print_item_preview
    )
    from test_runners.media_entertainment.test_configs import get_spotify_config
else:
    from ..utils import save_result, create_test_result, print_header
    from .media_utils import (
        check_spotify_credentials, merge_test_config,
        print_section_header, print_test_info, print_item_preview
    )
    from .test_configs import get_spotify_config


def _format_album(album: Dict, rank: int, original_rank: int = None) -> Dict:
    """标准化专辑输出，包含metadata和排序信息"""
    artist_names = [artist.get("name") for artist in album.get("artists", [])]
    release_date = album.get("release_date")

    formatted = {
        "answer": album.get("name"),
        "album_id": album.get("id"),
        "rank": rank,
        "album_type": album.get("album_type"),
        "release_date": release_date,
        "release_year": int(release_date.split("-")[0]) if release_date else None,
        "release_date_precision": album.get("release_date_precision"),
        "total_tracks": album.get("total_tracks"),
        "available_markets_count": len(album.get("available_markets", [])),
        "artist_names": artist_names,
        "is_collaboration": len(artist_names) > 1,
        "primary_artist": artist_names[0] if artist_names else None,
        "label": album.get("label"),
        "external_url": album.get("external_urls", {}).get("spotify"),
        "uri": album.get("uri"),
    }

    if original_rank is not None:
        formatted["original_rank"] = original_rank

    return formatted


def _format_track(track: Dict, rank: int, original_rank: int = None) -> Dict:
    """标准化曲目输出，包含metadata和排序信息"""
    duration_ms = track.get("duration_ms", 0)
    duration_minutes = duration_ms / 60000 if duration_ms else 0

    formatted = {
        "answer": track.get("name"),
        "track_id": track.get("id"),
        "rank": rank,
        "track_number": track.get("track_number"),
        "disc_number": track.get("disc_number"),
        "duration_ms": duration_ms,
        "duration_minutes": round(duration_minutes, 2),
        "explicit": track.get("explicit"),
        "is_playable": track.get("is_playable", True),
        "preview_url": track.get("preview_url"),
        "artists": [artist.get("name") for artist in track.get("artists", [])],
        "available_markets_count": len(track.get("available_markets", [])),
        "external_url": track.get("external_urls", {}).get("spotify"),
    }

    if original_rank is not None:
        formatted["original_rank"] = original_rank

    return formatted


def run(test_config=None):
    """运行Spotify API测试 - 展示真正的Enumerate All能力"""
    print_header("测试 Spotify API - 完整枚举")

    # 检查环境变量
    has_creds, skip_msg = check_spotify_credentials()
    if not has_creds:
        print(skip_msg)
        return []

    from fetchers.media_entertainment.spotify import SpotifyFetcher
    fetcher = SpotifyFetcher()

    # 加载配置 - 优先使用用户配置，否则使用默认配置
    default_config = get_spotify_config()
    config = merge_test_config(default_config, test_config) if test_config else default_config

    all_tests: List[Dict] = []

    for artist_info in config["artists"]:
        artist_id = artist_info["id"]
        artist_name = artist_info.get("name", artist_id)

        print_section_header("测试艺术家", f"{artist_name} ({artist_id})")

        try:
            # ============================================
            # 1. 获取所有专辑（完整metadata）
            # ============================================
            albums, api_info, question = fetcher.fetch_albums(artist_id)
            album_rank_map = {album.get("id"): idx + 1 for idx, album in enumerate(albums)}

            print_test_info("[1] 基础枚举:", question, len(albums))
            print_item_preview(albums, format_func=fetcher.format_album)

            base_answers = [
                _format_album(album, rank=idx + 1)
                for idx, album in enumerate(albums)
            ]

            all_tests.append(
                create_test_result(
                    question=question,
                    answers=base_answers,
                    api_info=api_info,
                    test_id=f"{artist_id}_all_albums",
                    query_category="basic_enumeration",
                    artist_id=artist_id,
                    artist_name=artist_name
                )
            )

            # ============================================
            # 2. 高级查询 - 合作专辑
            # ============================================
            collab_albums = fetcher.filter_collaboration_albums(albums)
            collab_question = f"列出Spotify艺术家 {artist_name} 的所有合作专辑"

            print_test_info("[2] 高级查询:", collab_question, len(collab_albums))
            if collab_albums:
                print_item_preview(collab_albums, format_func=fetcher.format_album)
            else:
                print("    (无合作专辑)")

            collab_answers = [
                _format_album(album, rank=idx + 1, original_rank=album_rank_map.get(album.get("id")))
                for idx, album in enumerate(collab_albums)
            ]

            all_tests.append(
                create_test_result(
                    question=collab_question,
                    answers=collab_answers,
                    api_info=api_info,
                    filter="artists>1",
                    test_id=f"{artist_id}_collaboration_albums",
                    query_category="advanced_filter",
                    artist_id=artist_id,
                    artist_name=artist_name
                )
            )

            # ============================================
            # 3. 高级查询 - 按年份筛选完整专辑
            # ============================================
            only_albums = fetcher.filter_albums_by_type(albums, "album")
            only_singles = fetcher.filter_albums_by_type(albums, "single")
            year_albums = fetcher.filter_albums_by_year(only_albums, year_start=2020)
            year_question = f"列出Spotify艺术家 {artist_name} 在2020年及之后发行的完整专辑"

            print_test_info("[3] 高级查询:", year_question, len(year_albums))
            if year_albums:
                print_item_preview(year_albums, format_func=fetcher.format_album)

            year_answers = [
                _format_album(album, rank=idx + 1, original_rank=album_rank_map.get(album.get("id")))
                for idx, album in enumerate(year_albums)
            ]

            all_tests.append(
                create_test_result(
                    question=year_question,
                    answers=year_answers,
                    api_info=api_info,
                    filter="album_type=album, release_year>=2020",
                    test_id=f"{artist_id}_albums_since_2020",
                    query_category="advanced_filter",
                    artist_id=artist_id,
                    artist_name=artist_name
                )
            )

            # ============================================
            # 4. 高级查询 - 按类型筛选
            # ============================================
            album_question = f"列出Spotify艺术家 {artist_name} 的所有完整专辑（不含单曲）"
            single_question = f"列出Spotify艺术家 {artist_name} 的所有单曲"

            print_test_info("[4a] 高级查询:", album_question, len(only_albums))
            if only_albums:
                print_item_preview(only_albums, format_func=fetcher.format_album)

            album_answers = [
                _format_album(album, rank=idx + 1, original_rank=album_rank_map.get(album.get("id")))
                for idx, album in enumerate(only_albums)
            ]

            all_tests.append(
                create_test_result(
                    question=album_question,
                    answers=album_answers,
                    api_info=api_info,
                    filter="album_type=album",
                    test_id=f"{artist_id}_studio_albums",
                    query_category="advanced_filter",
                    artist_id=artist_id,
                    artist_name=artist_name
                )
            )

            print_test_info("[4b] 高级查询:", single_question, len(only_singles))
            if only_singles:
                print_item_preview(only_singles, format_func=fetcher.format_album)

            single_answers = [
                _format_album(album, rank=idx + 1, original_rank=album_rank_map.get(album.get("id")))
                for idx, album in enumerate(only_singles)
            ]

            all_tests.append(
                create_test_result(
                    question=single_question,
                    answers=single_answers,
                    api_info=api_info,
                    filter="album_type=single",
                    test_id=f"{artist_id}_singles",
                    query_category="advanced_filter",
                    artist_id=artist_id,
                    artist_name=artist_name
                )
            )

            # ============================================
            # 5. 曲目级别查询（如果有专辑）
            # ============================================
            if albums:
                # 选择专辑《寓話γ》进行测试，如果找不到则使用第一张专辑
                test_album = next((a for a in albums if a.get("name") == "寓話γ"), None)
                if not test_album:
                    print("  (专项测试警告: 未在列表中找到专辑《寓話γ》。将使用找到的第一张适用专辑进行后续曲目测试。)")
                    test_album = next((a for a in albums if a.get("album_type") == "album"), albums[0])
                album_id = test_album.get("id")
                album_name = test_album.get("name")

                tracks, tracks_api_info, track_question = fetcher.fetch_tracks(album_id)
                track_rank_map = {track.get("id"): idx + 1 for idx, track in enumerate(tracks)}

                print_test_info("[5] 曲目枚举:", track_question, len(tracks))
                print_item_preview(tracks, format_func=fetcher.format_track)

                track_answers = [
                    _format_track(track, rank=idx + 1)
                    for idx, track in enumerate(tracks)
                ]

                all_tests.append(
                    create_test_result(
                        question=track_question,
                        answers=track_answers,
                        api_info=tracks_api_info,
                        album_id=album_id,
                        album_name=album_name,
                        test_id=f"{album_id}_all_tracks",
                        query_category="basic_enumeration",
                        artist_id=artist_id,
                        artist_name=artist_name
                    )
                )

                # 筛选长曲目（>5分钟）
                long_tracks = fetcher.filter_tracks_by_duration(tracks, min_ms=300000)
                long_track_question = f"列出专辑《{album_name}》中时长超过5分钟的曲目"

                print_test_info("[5b] 高级查询:", long_track_question, len(long_tracks))
                if long_tracks:
                    print_item_preview(long_tracks, format_func=fetcher.format_track)

                long_track_answers = [
                    _format_track(track, rank=idx + 1, original_rank=track_rank_map.get(track.get("id")))
                    for idx, track in enumerate(long_tracks)
                ]

                all_tests.append(
                    create_test_result(
                        question=long_track_question,
                        answers=long_track_answers,
                        api_info=tracks_api_info,
                        filter="duration_ms>=300000",
                        album_id=album_id,
                        album_name=album_name,
                        test_id=f"{album_id}_tracks_over_5_min",
                        query_category="advanced_filter",
                        artist_id=artist_id,
                        artist_name=artist_name
                    )
                )

        except Exception as exc:
            print(f"  ✗ 测试失败: {exc}")
            import traceback
            traceback.print_exc()

    # 保存完整结果（无截断）
    if all_tests:
        save_result(
            "media_entertainment/spotify",
            {
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
                "tests": all_tests
            }
        )

    print(f"\n{'='*60}")
    print(f"✓ Spotify测试完成 - 所有结果已完整枚举并保存")
    print(f"{'='*60}\n")

    return all_tests


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run()
