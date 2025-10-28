"""YouTube API 测试"""

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

    from fetchers.youtube import YouTubeFetcher
    fetcher = YouTubeFetcher()

    # 默认配置
    config = {
        "channels": [
            {"id": "UCYO_jab_esuFRV4b17AJtAw", "name": "3Blue1Brown"},
            {"id": "UCsooa4yRKGN_zEE8iknghZA", "name": "TED-Ed"}
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
            videos, api_info, question = fetcher.fetch_videos(
                channel_id,
                max_videos=config["max_videos"]
            )

            result = {
                "channel_id": channel_id,
                "channel_name": channel_name,
                "question": question,
                "api_info": api_info,
                "total_videos": len(videos),
                "sample_videos": videos[:10] if len(videos) > 10 else videos
            }
            results.append(result)

            print(f"  ✓ 找到 {len(videos)} 个视频")
            if len(videos) > 0:
                print(f"  前3个: {videos[:3]}")

        except Exception as e:
            print(f"  ✗ 测试失败: {e}")

    if results:
        save_result("youtube", {
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
