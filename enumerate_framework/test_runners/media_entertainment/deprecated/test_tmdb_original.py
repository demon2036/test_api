"""TMDb API 测试"""

import os
import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, print_header
else:
    from ..utils import save_result, print_header


def _load_env():
    """尝试加载 .env 文件中的环境变量"""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    # 先加载当前工作目录下的 .env，再加载项目目录下的 .env
    load_dotenv()
    project_env = Path(__file__).resolve().parents[2] / ".env"
    if project_env.exists():
        load_dotenv(project_env)


def run(test_config=None):
    """运行TMDb API测试

    Args:
        test_config: 测试配置字典，可包含:
            - persons: 要测试的人物列表（格式：[{"id": 31, "name": "Tom Hanks"}, ...]）
    """
    print_header("测试 TMDb API")

    # 默认配置
    config = {
        "persons": [
            {"id": 31, "name": "Tom Hanks"},
            {"id": 287, "name": "Brad Pitt"}
        ]
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    # 加载环境变量
    _load_env()

    # 检查环境变量
    api_key = os.getenv('TMDB_API_KEY')

    if not api_key:
        print("\n⚠️  跳过TMDb测试 - 缺少API Key")
        print("   请在.env文件中设置TMDB_API_KEY")
        print("   获取方式: https://www.themoviedb.org/settings/api")
        save_result("media_entertainment/tmdb", {
            "api_name": "TMDb",
            "requires_auth": True,
            "auth_type": "API Key",
            "status": "skipped",
            "reason": "缺少TMDB_API_KEY环境变量",
            "config": config,
            "tests": []
        })
        return []

    from fetchers.media_entertainment.tmdb import TMDbFetcher
    fetcher = TMDbFetcher()

    results = []

    for person_info in config["persons"]:
        person_id = person_info["id"]
        person_name = person_info.get("name", str(person_id))

        print(f"\n测试演员: {person_name} (person_id={person_id})")

        try:
            # 基础测试：获取所有作品
            credits, api_info, question = fetcher.fetch_person_credits(person_id)

            cast = credits.get("cast", [])
            crew = credits.get("crew", [])
            all_works = cast + crew

            result = {
                "person_id": person_id,
                "person_name": person_name,
                "question": question,
                "api_info": api_info,
                "total_credits": len(all_works),
                "sample_credits": all_works[:10] if len(all_works) > 10 else all_works,
                "total_cast": len(cast),
                "total_crew": len(crew),
                "sample_cast": cast[:5] if len(cast) > 5 else cast,
                "sample_crew": crew[:5] if len(crew) > 5 else crew
            }

            print(f"  ✓ 找到 {len(all_works)} 部作品")
            if len(all_works) > 0:
                preview = [fetcher.format_credit(item) for item in all_works[:3]]
                print(f"  前3部: {preview}")

            # ============================================
            # 高级测试
            # ============================================

            # 测试1：筛选同时担任演员和制片人的作品
            try:
                multi_role_works, _, multi_role_question = fetcher.filter_person_by_multiple_roles(
                    person_id,
                    "actor",
                    "producer"
                )
                result["actor_and_producer"] = {
                    "question": multi_role_question,
                    "total": len(multi_role_works),
                    "sample": multi_role_works[:5] if len(multi_role_works) > 5 else multi_role_works
                }
                print(f"  ✓ 找到 {len(multi_role_works)} 部同时担任演员和制片人的作品")
            except Exception as e:
                print(f"  ⚠ 多角色筛选失败: {e}")

            # 测试2：筛选科幻类型作品
            try:
                scifi_works, _, scifi_question = fetcher.filter_person_credits_by_genre(
                    person_id,
                    "science fiction"
                )
                result["science_fiction_works"] = {
                    "question": scifi_question,
                    "total": len(scifi_works),
                    "sample": scifi_works[:5] if len(scifi_works) > 5 else scifi_works
                }
                print(f"  ✓ 找到 {len(scifi_works)} 部科幻作品")
            except Exception as e:
                print(f"  ⚠ 类型筛选失败: {e}")

            # 测试3：喜剧类型作品
            try:
                comedy_works, _, comedy_question = fetcher.filter_person_credits_by_genre(
                    person_id,
                    "comedy"
                )
                result["comedy_works"] = {
                    "question": comedy_question,
                    "total": len(comedy_works),
                    "sample": comedy_works[:5] if len(comedy_works) > 5 else comedy_works
                }
                print(f"  ✓ 找到 {len(comedy_works)} 部喜剧作品")
            except Exception as e:
                print(f"  ⚠ 类型筛选失败: {e}")

            results.append(result)

        except Exception as e:
            print(f"  ✗ 测试失败: {e}")

    # 额外测试：TV剧集的客串明星筛选
    # 使用《权力的游戏》(Game of Thrones, TV ID: 1399) 第1季作为示例
    print(f"\n测试TV剧集客串筛选")
    try:
        tv_id = 1399  # Game of Thrones
        season_number = 1
        guest_episodes, api_info, guest_question = fetcher.filter_episodes_with_guest_stars(
            tv_id,
            season_number
        )
        tv_result = {
            "tv_id": tv_id,
            "tv_name": "Game of Thrones",
            "season": season_number,
            "question": guest_question,
            "api_info": api_info,
            "episodes_with_guests": len(guest_episodes),
            "sample": guest_episodes[:5] if len(guest_episodes) > 5 else guest_episodes
        }
        results.append(tv_result)
        print(f"  ✓ 找到 {len(guest_episodes)} 集有客串明星")
    except Exception as e:
        print(f"  ⚠ TV剧集测试失败: {e}")

    if results:
        save_result("media_entertainment/tmdb", {
            "api_name": "TMDb",
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
