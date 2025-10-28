"""TMDb API 测试"""

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
    """运行TMDb API测试

    Args:
        test_config: 测试配置字典，可包含:
            - persons: 要测试的人物列表（格式：[{"id": 31, "name": "Tom Hanks"}, ...]）
    """
    print_header("测试 TMDb API")

    # 检查环境变量
    api_key = os.getenv('TMDB_API_KEY')

    if not api_key:
        print("\n⚠️  跳过TMDb测试 - 缺少API Key")
        print("   请在.env文件中设置TMDB_API_KEY")
        print("   获取方式: https://www.themoviedb.org/settings/api")
        return []

    from fetchers.tmdb import TMDbFetcher
    fetcher = TMDbFetcher()

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

    results = []

    for person_info in config["persons"]:
        person_id = person_info["id"]
        person_name = person_info.get("name", str(person_id))

        print(f"\n测试演员: {person_name} (person_id={person_id})")

        try:
            credits, api_info, question = fetcher.fetch_person_credits(person_id)

            result = {
                "person_id": person_id,
                "person_name": person_name,
                "question": question,
                "api_info": api_info,
                "total_credits": len(credits),
                "sample_credits": credits[:10] if len(credits) > 10 else credits
            }
            results.append(result)

            print(f"  ✓ 找到 {len(credits)} 部作品")
            if len(credits) > 0:
                print(f"  前3部: {credits[:3]}")

        except Exception as e:
            print(f"  ✗ 测试失败: {e}")

    if results:
        save_result("tmdb", {
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
