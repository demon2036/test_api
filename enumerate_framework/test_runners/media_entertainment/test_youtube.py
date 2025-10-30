"""YouTube API 测试"""

import sys
from pathlib import Path
from typing import Dict, List

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
    from test_runners.media_entertainment.media_utils import (
        check_youtube_credentials, print_section_header, print_test_info
    )
    from test_runners.media_entertainment.test_configs import get_youtube_config
else:
    from ..utils import save_result, create_test_result, print_header
    from .media_utils import (
        check_youtube_credentials, print_section_header, print_test_info
    )
    from .test_configs import get_youtube_config


def _format_video_item(video: Dict, rank: int, original_rank: int = None) -> Dict:
    """标准化视频输出，确保包含metadata与排序信息"""
    snippet = video.get("snippet", {})
    statistics = video.get("statistics", {}) or {}
    content_details = video.get("contentDetails", {}) or {}
    published_at = snippet.get("publishedAt")

    formatted = {
        "answer": snippet.get("title"),
        "video_id": video.get("id"),
        "rank": rank,
        "original_rank": original_rank,
        "channel_title": snippet.get("channelTitle"),
        "channel_id": video.get("_channel_id"),
        "published_at": published_at,
        "published_date": published_at[:10] if published_at else None,
        "duration_iso8601": content_details.get("duration"),
        "duration_seconds": video.get("duration_seconds"),
        "duration_minutes": video.get("duration_minutes"),
        "view_count": video.get("view_count"),
        "like_count": int(statistics.get("likeCount", 0)) if statistics.get("likeCount") is not None else None,
        "comment_count": int(statistics.get("commentCount", 0)) if statistics.get("commentCount") is not None else None,
        "favorite_count": int(statistics.get("favoriteCount", 0)) if statistics.get("favoriteCount") is not None else None,
        "tags": snippet.get("tags", []),
        "category_id": snippet.get("categoryId"),
        "live_broadcast": snippet.get("liveBroadcastContent"),
        "default_language": snippet.get("defaultLanguage"),
        "default_audio_language": snippet.get("defaultAudioLanguage"),
        "definition": content_details.get("definition"),
        "caption": content_details.get("caption"),
        "licensed_content": content_details.get("licensedContent"),
        "projection": content_details.get("projection"),
        "thumbnail_default": snippet.get("thumbnails", {}).get("default", {}).get("url"),
        "thumbnail_high": snippet.get("thumbnails", {}).get("high", {}).get("url"),
        "description": snippet.get("description"),
        "url": video.get("url")
    }

    # 移除 None 值，使输出更紧凑
    return {k: v for k, v in formatted.items() if v not in (None, [], {})}


def run(test_config=None):
    """运行YouTube API测试"""
    print_header("测试 YouTube API")

    # 检查环境变量
    has_creds, skip_msg = check_youtube_credentials()
    if not has_creds:
        print(skip_msg)
        return []

    from fetchers.media_entertainment.youtube import YouTubeFetcher
    fetcher = YouTubeFetcher()

    config = test_config if test_config else get_youtube_config()
    tests: List[Dict] = []

    for channel_info in config["channels"]:
        channel_id = channel_info["id"]
        channel_name = channel_info.get("name", channel_id)

        print_section_header("测试频道", f"{channel_name} ({channel_id})")

        try:
            videos, api_info, question = fetcher.fetch_videos(channel_id)
            enhanced_videos = [fetcher.add_video_metadata(v) for v in videos]

            # 确保稳定排序：按发布时间降序，再按ID
            enhanced_videos.sort(
                key=lambda v: (
                    v.get("snippet", {}).get("publishedAt", ""),
                    v.get("id", "")
                ),
                reverse=True
            )

            video_rank_map = {video.get("id"): idx + 1 for idx, video in enumerate(enhanced_videos)}

            base_answers = [
                _format_video_item(video, rank=idx + 1)
                for idx, video in enumerate(enhanced_videos)
            ]

            channel_display = (
                f"{enhanced_videos[0].get('_channel_name')} ({channel_id})"
                if enhanced_videos else f"{channel_name} ({channel_id})"
            )

            print_test_info("[1] 基础枚举:", question, len(base_answers))

            tests.append(
                create_test_result(
                    question=question,
                    answers=base_answers,
                    api_info=api_info,
                    channel_id=channel_id,
                    channel_name=channel_display,
                    test_id=f"{channel_id}_all_videos",
                    query_category="basic_enumeration"
                )
            )

            # ============================================
            # 高级测试：筛选长视频
            # ============================================
            try:
                long_videos = fetcher.filter_videos_by_duration(enhanced_videos, min_seconds=3600)
                long_video_answers = [
                    _format_video_item(video, rank=idx + 1, original_rank=video_rank_map.get(video.get("id")))
                    for idx, video in enumerate(long_videos)
                ]

                question_long = f"筛选频道 {channel_display} 中时长超过60分钟的视频"
                print_test_info("[2] 高级查询:", question_long, len(long_videos))

                tests.append(
                    create_test_result(
                        question=question_long,
                        answers=long_video_answers,
                        api_info=api_info,
                        filter="duration_seconds>=3600",
                        channel_id=channel_id,
                        channel_name=channel_display,
                        test_id=f"{channel_id}_videos_over_60min",
                        query_category="advanced_filter"
                    )
                )
            except Exception as exc:
                print(f"  ⚠ 时长筛选失败: {exc}")

            # ============================================
            # 高级测试：观看次数最多的视频
            # ============================================
            try:
                most_viewed = fetcher.get_most_viewed_video(enhanced_videos)
                if most_viewed:
                    question_most = f"找出频道 {channel_display} 中观看次数最多的视频"
                    print_test_info("[3] 高级查询:", question_most, 1)

                    most_viewed_answer = _format_video_item(
                        most_viewed,
                        rank=1,
                        original_rank=video_rank_map.get(most_viewed.get("id"))
                    )

                    tests.append(
                        create_test_result(
                            question=question_most,
                            answers=[most_viewed_answer],
                            api_info=api_info,
                            filter="max(view_count)",
                            channel_id=channel_id,
                            channel_name=channel_display,
                            test_id=f"{channel_id}_most_viewed",
                            query_category="advanced_filter"
                        )
                    )
            except Exception as exc:
                print(f"  ⚠ 最多观看筛选失败: {exc}")

            # ============================================
            # 高级测试：观看次数超过100万
            # ============================================
            try:
                popular_videos = fetcher.filter_videos_by_views(enhanced_videos, min_views=1_000_000)
                popular_answers = [
                    _format_video_item(video, rank=idx + 1, original_rank=video_rank_map.get(video.get("id")))
                    for idx, video in enumerate(popular_videos)
                ]

                question_popular = f"筛选频道 {channel_display} 中观看次数超过100万的视频"
                print_test_info("[4] 高级查询:", question_popular, len(popular_videos))

                tests.append(
                    create_test_result(
                        question=question_popular,
                        answers=popular_answers,
                        api_info=api_info,
                        filter="view_count>=1000000",
                        channel_id=channel_id,
                        channel_name=channel_display,
                        test_id=f"{channel_id}_videos_over_1m_views",
                        query_category="advanced_filter"
                    )
                )
            except Exception as exc:
                print(f"  ⚠ 观看次数筛选失败: {exc}")

            # ============================================
            # 高级测试：关键词搜索
            # ============================================
            try:
                keywords = ["不可解", "Incomprehensible", "FUKAKAI"]
                keyword_videos = [
                    fetcher.add_video_metadata(video)
                    for video in videos
                    if any(kw.lower() in video['snippet']['title'].lower() for kw in keywords)
                ]

                keyword_answers = [
                    _format_video_item(video, rank=idx + 1, original_rank=video_rank_map.get(video.get("id")))
                    for idx, video in enumerate(keyword_videos)
                ]

                question_keyword = f"搜索频道 {channel_display} 中包含'不可解/Incomprehensible'关键词的视频"
                print_test_info("[5] 高级查询:", question_keyword, len(keyword_videos))

                tests.append(
                    create_test_result(
                        question=question_keyword,
                        answers=keyword_answers,
                        api_info=api_info,
                        filter="keyword=不可解|Incomprehensible|FUKAKAI",
                        channel_id=channel_id,
                        channel_name=channel_display,
                        test_id=f"{channel_id}_keyword_incomprehensible",
                        query_category="advanced_filter"
                    )
                )
            except Exception as exc:
                print(f"  ⚠ 关键词搜索失败: {exc}")

        except Exception as exc:
            print(f"  ✗ 测试失败: {exc}")

    if tests:
        save_result(
            "media_entertainment/youtube",
            {
                "api_name": "YouTube",
                "requires_auth": True,
                "auth_type": "API Key",
                "config": config,
                "tests": tests
            }
        )

    return tests


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run()
