"""TMDb API 测试"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
    from test_runners.media_entertainment.media_utils import (
        check_tmdb_credentials, load_env_file, create_skip_result,
        print_section_header, print_test_info, print_item_preview
    )
    from test_runners.media_entertainment.test_configs import get_tmdb_config
else:
    from ..utils import save_result, create_test_result, print_header
    from .media_utils import (
        check_tmdb_credentials, load_env_file, create_skip_result,
        print_section_header, print_test_info, print_item_preview
    )
    from .test_configs import get_tmdb_config


GENRE_LOOKUP: Dict[int, str] = {}


def _ensure_genre_lookup():
    """构建类型ID到名称的映射表"""
    global GENRE_LOOKUP
    if GENRE_LOOKUP:
        return

    try:
        from fetchers.media_entertainment.tmdb import TMDB_GENRES, TMDB_GENRES_EN
    except ImportError:
        GENRE_LOOKUP = {}
        return

    # 优先使用中文名称，缺失时回退到英文名称
    combined = {}
    combined.update({gid: name for gid, name in TMDB_GENRES.items()})
    combined.update({gid: TMDB_GENRES_EN.get(gid, name) for gid, name in TMDB_GENRES.items()})
    # 追加英文映射
    combined.update({gid: name for gid, name in TMDB_GENRES_EN.items()})

    GENRE_LOOKUP = combined


def _infer_credit_type(credit: Dict) -> str:
    """根据字段判断该作品属于演员还是幕后"""
    if credit.get("media_type") == "person":
        return "crew"
    if credit.get("character") or credit.get("order") is not None:
        return "cast"
    return "crew"


def _build_tmdb_url(media_type: str, item_id: int) -> str:
    """构建可浏览的TMDb详情页链接"""
    if not media_type or item_id is None:
        return ""
    if media_type == "movie":
        return f"https://www.themoviedb.org/movie/{item_id}"
    if media_type == "tv":
        return f"https://www.themoviedb.org/tv/{item_id}"
    return f"https://www.themoviedb.org/{media_type}/{item_id}"


def _format_credit_item(
    credit: Dict,
    credit_type: str,
    rank: int,
    original_rank: int = None
) -> Dict:
    """标准化作品输出，包含metadata和排序信息"""
    release_date = credit.get("release_date") or credit.get("first_air_date")
    release_year = int(release_date[:4]) if release_date and release_date[:4].isdigit() else None
    media_type = credit.get("media_type")
    genre_ids = credit.get("genre_ids", []) or []
    _ensure_genre_lookup()
    genres = [GENRE_LOOKUP.get(gid, str(gid)) for gid in genre_ids]

    formatted = {
        "answer": credit.get("title") or credit.get("name"),
        "credit_id": credit.get("credit_id"),
        "tmdb_id": credit.get("id"),
        "media_type": media_type,
        "credit_type": credit_type,
        "rank": rank,
        "original_rank": original_rank,
        "release_date": release_date,
        "release_year": release_year,
        "vote_average": credit.get("vote_average"),
        "vote_count": credit.get("vote_count"),
        "popularity": credit.get("popularity"),
        "character": credit.get("character"),
        "job": credit.get("job"),
        "department": credit.get("department"),
        "known_for_department": credit.get("known_for_department"),
        "origin_country": credit.get("origin_country"),
        "original_language": credit.get("original_language"),
        "genres": genres,
        "genre_ids": genre_ids,
        "poster_path": credit.get("poster_path"),
        "backdrop_path": credit.get("backdrop_path"),
        "overview": credit.get("overview"),
        "order": credit.get("order"),
        "episode_count": credit.get("episode_count"),
        "adult": credit.get("adult"),
        "tmdb_url": _build_tmdb_url(media_type, credit.get("id"))
    }

    # 清理 None 值，提高可读性
    return {k: v for k, v in formatted.items() if v not in (None, [], {})}


def _format_combined_role_item(
    work: Dict,
    rank: int,
    primary_rank: int = None,
    secondary_rank: int = None
) -> Dict:
    """格式化同时担任多个角色的作品"""
    primary_meta = work.get("primary_metadata", {}) or {}
    secondary_meta = work.get("secondary_metadata", {}) or {}
    release_date = (
        primary_meta.get("release_date")
        or primary_meta.get("first_air_date")
        or secondary_meta.get("release_date")
        or secondary_meta.get("first_air_date")
    )
    media_type = work.get("media_type") or primary_meta.get("media_type") or secondary_meta.get("media_type")
    genre_ids = primary_meta.get("genre_ids") or secondary_meta.get("genre_ids") or []
    _ensure_genre_lookup()
    genres = [GENRE_LOOKUP.get(gid, str(gid)) for gid in genre_ids]

    formatted = {
        "answer": work.get("title"),
        "tmdb_id": work.get("id"),
        "media_type": media_type,
        "rank": rank,
        "primary_role": work.get("primary_role"),
        "secondary_role": work.get("secondary_role"),
        "primary_rank": primary_rank,
        "secondary_rank": secondary_rank,
        "release_date": release_date,
        "vote_average": primary_meta.get("vote_average") or secondary_meta.get("vote_average"),
        "vote_count": primary_meta.get("vote_count") or secondary_meta.get("vote_count"),
        "character": primary_meta.get("character"),
        "job": secondary_meta.get("job"),
        "department": secondary_meta.get("department"),
        "genres": genres,
        "genre_ids": genre_ids,
        "poster_path": primary_meta.get("poster_path") or secondary_meta.get("poster_path"),
        "overview": primary_meta.get("overview") or secondary_meta.get("overview"),
        "tmdb_url": _build_tmdb_url(media_type, work.get("id"))
    }

    return {k: v for k, v in formatted.items() if v not in (None, [], {})}


def _format_episode_item(episode: Dict, rank: int) -> Dict:
    """格式化剧集信息，包含客串明星metadata"""
    guest_stars = episode.get("guest_stars", []) or []
    formatted = {
        "answer": f"S{episode.get('season_number', 0):02d}E{episode.get('episode_number', 0):02d} {episode.get('name')}",
        "episode_id": episode.get("id"),
        "rank": rank,
        "season": episode.get("season_number"),
        "episode_number": episode.get("episode_number"),
        "air_date": episode.get("air_date"),
        "runtime": episode.get("runtime"),
        "vote_average": episode.get("vote_average"),
        "vote_count": episode.get("vote_count"),
        "guest_star_count": len(guest_stars),
        "guest_stars": [
            {
                "name": gs.get("name"),
                "character": gs.get("character"),
                "order": gs.get("order"),
                "tmdb_id": gs.get("id")
            }
            for gs in guest_stars
        ],
        "overview": episode.get("overview"),
        "still_path": episode.get("still_path"),
        "tmdb_url": f"https://www.themoviedb.org/tv/{episode.get('show_id')}/season/{episode.get('season_number')}/episode/{episode.get('episode_number')}"
        if episode.get("show_id") and episode.get("season_number") and episode.get("episode_number")
        else None
    }
    return {k: v for k, v in formatted.items() if v not in (None, [], {})}


def run(test_config=None):
    """运行TMDb API测试"""
    print_header("测试 TMDb API")

    # 加载环境变量
    load_env_file()

    # 检查环境变量
    has_creds, skip_msg = check_tmdb_credentials()
    if not has_creds:
        print(skip_msg)
        config = test_config if test_config else get_tmdb_config()
        save_result(
            "media_entertainment/tmdb",
            create_skip_result("TMDb", "API Key", config, "缺少TMDB_API_KEY环境变量")
        )
        return []

    from fetchers.media_entertainment.tmdb import TMDbFetcher
    fetcher = TMDbFetcher()

    config = test_config if test_config else get_tmdb_config()
    tests: List[Dict] = []

    for person_info in config["persons"]:
        person_id = person_info["id"]
        person_name = person_info.get("name", str(person_id))

        print_section_header("测试演员", f"{person_name} (person_id={person_id})")

        try:
            credits_data, api_info, _ = fetcher.fetch_person_credits(person_id)
            question = f"列出TMDb人物 {person_name} (ID: {person_id}) 的所有影视作品"
            cast = credits_data.get("cast", [])
            crew = credits_data.get("crew", [])

            combined: List[Tuple[Dict, str]] = [(item, "cast") for item in cast] + [(item, "crew") for item in crew]
            # 按发行日期降序排序，保持确定性
            combined.sort(
                key=lambda item: (
                    (item[0].get("release_date") or item[0].get("first_air_date") or ""),
                    item[0].get("title") or item[0].get("name") or "",
                    item[0].get("id") or 0,
                    item[1]
                ),
                reverse=True
            )

            rank_map = {}
            base_answers = []
            for idx, (credit, credit_type) in enumerate(combined, start=1):
                formatted = _format_credit_item(credit, credit_type, rank=idx)
                base_answers.append(formatted)
                rank_map[(credit_type, credit.get("id"))] = idx

            print_test_info("[1] 基础枚举:", question, len(base_answers))
            print_item_preview(combined, format_func=lambda item: fetcher.format_credit(item[0]))

            tests.append(
                create_test_result(
                    question=question,
                    answers=base_answers,
                    api_info=api_info,
                    person_id=person_id,
                    person_name=person_name,
                    test_id=f"{person_id}_all_credits",
                    query_category="basic_enumeration"
                )
            )

            # ============================================
            # 高级查询：演员兼制片人
            # ============================================
            try:
                multi_role_works, _, _ = fetcher.filter_person_by_multiple_roles(
                    person_id,
                    "actor",
                    "producer"
                )
                multi_role_question = f"筛选TMDb人物 {person_name} (ID: {person_id}) 同时作为演员和制片人的所有作品"
                print_test_info("[2] 高级查询:", multi_role_question, len(multi_role_works))

                multi_role_answers = []
                for idx, work in enumerate(multi_role_works, start=1):
                    primary_rank = rank_map.get(("cast", work.get("id")))
                    secondary_rank = rank_map.get(("crew", work.get("id")))
                    multi_role_answers.append(
                        _format_combined_role_item(
                            work,
                            rank=idx,
                            primary_rank=primary_rank,
                            secondary_rank=secondary_rank
                        )
                    )

                tests.append(
                    create_test_result(
                        question=multi_role_question,
                        answers=multi_role_answers,
                        api_info=api_info,
                        filter="roles=actor+producer",
                        person_id=person_id,
                        person_name=person_name,
                        test_id=f"{person_id}_actor_and_producer",
                        query_category="advanced_filter"
                    )
                )
            except Exception as exc:
                print(f"  ⚠ 多角色筛选失败: {exc}")

            # ============================================
            # 高级查询：科幻类型作品
            # ============================================
            try:
                scifi_works, _, _ = fetcher.filter_person_credits_by_genre(
                    person_id,
                    "science fiction"
                )
                scifi_question = f"筛选TMDb人物 {person_name} (ID: {person_id}) 的所有科幻类影视作品"
                print_test_info("[3] 高级查询:", scifi_question, len(scifi_works))
                if scifi_works:
                    print_item_preview(scifi_works, format_func=fetcher.format_credit)

                scifi_answers = []
                for idx, credit in enumerate(scifi_works, start=1):
                    credit_type = _infer_credit_type(credit)
                    original_rank = rank_map.get((credit_type, credit.get("id")))
                    formatted = _format_credit_item(credit, credit_type, rank=idx, original_rank=original_rank)
                    formatted["matched_genre"] = "Science Fiction"
                    scifi_answers.append(formatted)

                tests.append(
                    create_test_result(
                        question=scifi_question,
                        answers=scifi_answers,
                        api_info=api_info,
                        filter="genre=science fiction",
                        person_id=person_id,
                        person_name=person_name,
                        test_id=f"{person_id}_science_fiction",
                        query_category="advanced_filter"
                    )
                )
            except Exception as exc:
                print(f"  ⚠ 类型筛选失败: {exc}")

            # ============================================
            # 高级查询：喜剧类型作品
            # ============================================
            try:
                comedy_works, _, _ = fetcher.filter_person_credits_by_genre(
                    person_id,
                    "comedy"
                )
                comedy_question = f"筛选TMDb人物 {person_name} (ID: {person_id}) 的所有喜剧类影视作品"
                print_test_info("[4] 高级查询:", comedy_question, len(comedy_works))
                if comedy_works:
                    print_item_preview(comedy_works, format_func=fetcher.format_credit)

                comedy_answers = []
                for idx, credit in enumerate(comedy_works, start=1):
                    credit_type = _infer_credit_type(credit)
                    original_rank = rank_map.get((credit_type, credit.get("id")))
                    formatted = _format_credit_item(credit, credit_type, rank=idx, original_rank=original_rank)
                    formatted["matched_genre"] = "Comedy"
                    comedy_answers.append(formatted)

                tests.append(
                    create_test_result(
                        question=comedy_question,
                        answers=comedy_answers,
                        api_info=api_info,
                        filter="genre=comedy",
                        person_id=person_id,
                        person_name=person_name,
                        test_id=f"{person_id}_comedy",
                        query_category="advanced_filter"
                    )
                )
            except Exception as exc:
                print(f"  ⚠ 类型筛选失败: {exc}")

        except Exception as exc:
            print(f"  ✗ 测试失败: {exc}")

    # 额外测试：TV剧集的客串明星筛选
    print_section_header("测试TV剧集客串筛选", "Game of Thrones S1")
    try:
        tv_id = 1399  # Game of Thrones
        season_number = 1
        guest_episodes, api_info, _ = fetcher.filter_episodes_with_guest_stars(
            tv_id,
            season_number
        )
        guest_question = f"筛选电视剧《权力的游戏》(ID: {tv_id}) 第 {season_number} 季中有客串明星的所有剧集"

        print_test_info("[5] 高级查询:", guest_question, len(guest_episodes))
        if guest_episodes:
            print_item_preview(guest_episodes, format_func=fetcher.format_episode)

        episode_answers = [
            _format_episode_item(
                {**episode, "show_id": tv_id},
                rank=idx + 1
            )
            for idx, episode in enumerate(guest_episodes)
        ]

        tests.append(
            create_test_result(
                question=guest_question,
                answers=episode_answers,
                api_info=api_info,
                filter="guest_stars>0",
                tv_id=tv_id,
                season_number=season_number,
                test_id=f"{tv_id}_season_{season_number}_guest_stars",
                query_category="advanced_filter"
            )
        )
    except Exception as exc:
        print(f"  ⚠ TV剧集测试失败: {exc}")

    if tests:
        save_result(
            "media_entertainment/tmdb",
            {
                "api_name": "TMDb",
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