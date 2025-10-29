"""YouTube API 测试"""

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
    """运行YouTube API测试

    Args:
        test_config: 测试配置字典，可包含:
            - channels: 要测试的频道列表（格式：[{"id": "...", "name": "..."}, ...]）
            - max_videos: 每个频道最多获取多少视频
    """
    print_header("测试 YouTube API")

    # 检查环境变量
    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key:
        print("\n⚠️  跳过YouTube测试 - 缺少API Key")
        print("   请在.env文件中设置YOUTUBE_API_KEY")
        print("   获取方式: https://console.cloud.google.com/apis/credentials")
        return []

    from fetchers.media_entertainment.youtube import YouTubeFetcher
    fetcher = YouTubeFetcher()

    # 默认配置
    config = {
        "channels": [
            {"id": "UCQ1U65-CQdIoZ2_NA4Z4F7A", "name": "花譜 / KAF (官方频道)"},
            {"id": "UCAOhUv73jM5iCpOhuJOQzxA", "name": "KAMITSUBAKI STUDIO"}
        ],
        "max_videos": 200
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    for channel_info in config["channels"]:
        channel_id = channel_info["id"]
        channel_name = channel_info.get("name", channel_id)

        print(f"\n测试频道: {channel_name} ({channel_id})")

        try:
            # 基础测试：获取所有视频（完整metadata）
            videos, api_info, question = fetcher.fetch_videos(channel_id)

            # 从视频中提取频道信息（如果可用）
            if videos and len(videos) > 0:
                actual_channel_name = videos[0].get('_channel_name', channel_name)
                channel_display = f"{actual_channel_name} ({channel_id})"
            else:
                channel_display = f"{channel_name} ({channel_id})"

            # 格式化前3个视频以便预览
            preview_videos = []
            for v in videos[:3]:
                title = v['snippet']['title']
                date = v['snippet']['publishedAt'][:10]
                view_count = int(v.get('statistics', {}).get('viewCount', 0))
                preview_videos.append(f"{title} ({date}) - {view_count:,} views")

            # 创建简化的样本视频列表（添加元信息）
            sample_videos = []
            for v in videos[:5]:
                enhanced = fetcher.add_video_metadata(v)
                sample_videos.append({
                    "title": enhanced['snippet']['title'],
                    "video_id": enhanced['id'],
                    "url": enhanced['url'],
                    "published_at": enhanced['snippet']['publishedAt'][:10],
                    "view_count": enhanced['view_count'],
                    "duration_seconds": enhanced['duration_seconds'],
                    "duration_minutes": enhanced['duration_minutes']
                })

            result = {
                "channel_id": channel_id,
                "channel_name": channel_name,
                "question": question,
                "api_info": api_info,
                "total_videos": len(videos),
                "sample_videos": sample_videos
            }

            print(f"  ✓ 找到 {len(videos)} 个视频")
            if len(preview_videos) > 0:
                print(f"  前3个视频:")
                for pv in preview_videos:
                    print(f"    - {pv}")

            # ============================================
            # 高级测试：基于metadata的筛选
            # ============================================

            # 测试1：筛选时长超过60分钟的视频
            try:
                long_videos = fetcher.filter_videos_by_duration(
                    videos,
                    min_seconds=3600  # 60分钟 = 3600秒
                )

                # 创建简化的答案列表，只包含关键信息
                answer_list = [
                    {
                        "title": v['snippet']['title'],
                        "video_id": v['id'],
                        "url": v['url'],
                        "published_at": v['snippet']['publishedAt'][:10],
                        "duration_seconds": v['duration_seconds'],
                        "duration_minutes": v['duration_minutes'],
                        "view_count": v['view_count']
                    }
                    for v in long_videos
                ]

                result["long_videos"] = {
                    "question": f"筛选频道 {channel_display} 中时长超过60分钟的视频",
                    "total": len(long_videos),
                    "answer": answer_list
                }
                print(f"  ✓ 找到 {len(long_videos)} 个超过60分钟的视频")
                if len(long_videos) > 0:
                    print(f"  示例:")
                    for v in long_videos[:3]:
                        print(f"    - {v['snippet']['title'][:50]}... ({v['duration_minutes']}分钟)")
            except Exception as e:
                print(f"  ⚠ 时长筛选失败: {e}")

            # 测试2：找出观看次数最多的视频
            try:
                most_viewed = fetcher.get_most_viewed_video(videos)
                if most_viewed:
                    result["most_viewed_video"] = {
                        "question": f"找出频道 {channel_display} 中观看次数最多的视频",
                        "answer": {
                            "title": most_viewed['snippet']['title'],
                            "video_id": most_viewed['id'],
                            "url": most_viewed['url'],
                            "view_count": most_viewed['view_count'],
                            "duration_seconds": most_viewed['duration_seconds'],
                            "duration_minutes": most_viewed['duration_minutes'],
                            "published_at": most_viewed['snippet']['publishedAt'][:10]
                        }
                    }
                    print(f"  ✓ 观看最多的视频: {most_viewed['snippet']['title']} ({most_viewed['view_count']:,} views)")
            except Exception as e:
                print(f"  ⚠ 最多观看筛选失败: {e}")

            # 测试3：筛选高观看量视频（超过100万次）
            try:
                popular_videos = fetcher.filter_videos_by_views(
                    videos,
                    min_views=1000000  # 100万次观看
                )

                # 创建简化的答案列表
                answer_list = [
                    {
                        "title": v['snippet']['title'],
                        "video_id": v['id'],
                        "url": v['url'],
                        "published_at": v['snippet']['publishedAt'][:10],
                        "view_count": v['view_count'],
                        "duration_seconds": v['duration_seconds'],
                        "duration_minutes": v['duration_minutes']
                    }
                    for v in popular_videos
                ]

                result["popular_videos"] = {
                    "question": f"筛选频道 {channel_display} 中观看次数超过100万的视频",
                    "total": len(popular_videos),
                    "answer": answer_list
                }
                print(f"  ✓ 找到 {len(popular_videos)} 个超过100万观看的视频")
            except Exception as e:
                print(f"  ⚠ 观看次数筛选失败: {e}")

            # 测试4：搜索特定关键词视频 (如"不可解" / "Incomprehensible")
            try:
                keywords = ["不可解", "Incomprehensible", "FUKAKAI"]
                keyword_videos = []
                for v in videos:
                    title = v['snippet']['title']
                    if any(kw in title or kw.lower() in title.lower() for kw in keywords):
                        keyword_videos.append(v)

                if keyword_videos:
                    result["incomprehensible_videos"] = {
                        "question": f"搜索频道 {channel_display} 中包含'不可解/Incomprehensible'的视频",
                        "total": len(keyword_videos),
                        "videos": [
                            {
                                "title": v['snippet']['title'],
                                "views": int(v.get('statistics', {}).get('viewCount', 0)),
                                "url": f"https://www.youtube.com/watch?v={v['id']}",
                                "published": v['snippet']['publishedAt'][:10]
                            }
                            for v in keyword_videos
                        ]
                    }
                    print(f"  ✓ 找到 {len(keyword_videos)} 个'不可解/Incomprehensible'相关视频")
                    for kv in keyword_videos[:3]:
                        title = kv['snippet']['title']
                        views = int(kv.get('statistics', {}).get('viewCount', 0))
                        print(f"    - {title[:50]}... ({views:,} views)")
            except Exception as e:
                print(f"  ⚠ 关键词搜索失败: {e}")

            results.append(result)

        except Exception as e:
            print(f"  ✗ 测试失败: {e}")

    if results:
        save_result("media_entertainment/youtube", {
            "api_name": "YouTube",
            "requires_auth": True,
            "auth_type": "API Key",
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
