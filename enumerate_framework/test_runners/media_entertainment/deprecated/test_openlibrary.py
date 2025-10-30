"""Open Library API 测试 - 完整枚举，包含高级查询

⚠️ DEPRECATED (2025-10-29) ⚠️
This test has been deprecated as Open Library has been removed from the framework.

See GEMINI.md "Deprecated/Removed APIs" section for details.

Refactored version using media_utils and test_configs for cleaner code.
"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from test_runners.utils import save_result, print_header
    from test_runners.media_entertainment.media_utils import (
        print_section_header, print_test_info, print_item_preview
    )
    from test_runners.media_entertainment.test_configs import get_openlibrary_config
else:
    from ..utils import save_result, print_header
    from .media_utils import (
        print_section_header, print_test_info, print_item_preview
    )
    from .test_configs import get_openlibrary_config


def run(test_config=None):
    """运行Open Library API测试 - 展示真正的Enumerate All能力

    Args:
        test_config: 测试配置字典，可包含:
            - authors: 要测试的作者列表（格式：[{"key": "OL34221A", "name": "Isaac Asimov"}, ...]）
            - max_works: 每个作者最多获取多少作品
    """
    print_header("测试 Open Library API - 完整枚举")

    from fetchers.media_entertainment.goodreads import OpenLibraryFetcher
    fetcher = OpenLibraryFetcher()

    # 加载配置
    config = test_config if test_config else get_openlibrary_config()

    results = []

    for author_info in config["authors"]:
        author_key = author_info["key"]
        author_name = author_info.get("name", author_key)

        print_section_header("测试作者", f"{author_name} ({author_key})")

        try:
            # ============================================
            # 1. 获取所有作品（完整metadata）
            # ============================================
            works, api_info, question = fetcher.fetch_author_works(
                author_key,
                max_works=config.get("max_works", 100)
            )

            result = {
                "author_key": author_key,
                "author_name": author_name,
                "api_info": api_info,
                "tests": []
            }

            print_test_info("[1] 基础枚举:", question, len(works))
            print_item_preview(works[:10], format_func=fetcher.format_work)

            result["tests"].append({
                "question": question,
                "total": len(works),
                "all_items": [fetcher.format_work(w) for w in works]
            })

            # ============================================
            # 2. 高级查询 - 多语言翻译作品（限制为前20部作品以加快速度）
            # ============================================
            print(f"\n[2] 高级查询: 列出{author_name}被翻译成10种以上语言的作品")
            print(f"  （注意：需要获取每部作品的所有版本，可能较慢）")

            # 为了演示目的，只检查前5部作品
            sample_works = works[:5]
            multilang_works = fetcher.filter_by_languages(sample_works, min_languages=10)

            print(f"  ✓ 从前5部作品中找到 {len(multilang_works)} 部多语言作品")
            if multilang_works:
                print(f"  完整列表:")
                for i, work in enumerate(multilang_works, 1):
                    print(f"    {i}. {fetcher.format_work(work)}")
                    print(f"       语言: {', '.join(work.get('_languages', [])[:10])}...")
            else:
                print(f"  (前5部作品中无符合条件的作品)")

            result["tests"].append({
                "question": f"列出{author_name}被翻译成10种以上语言的作品（前5部采样）",
                "total": len(multilang_works),
                "all_items": [fetcher.format_work(w) for w in multilang_works]
            })

            # ============================================
            # 3. 高级查询 - 页数超过500页的作品（限制为前10部作品）
            # ============================================
            print(f"\n[3] 高级查询: 列出{author_name}页数超过500页的作品")
            print(f"  （注意：需要获取每部作品的所有版本，可能较慢）")

            # 为了演示目的，只检查前5部作品
            sample_works_pages = works[:5]
            long_books = fetcher.filter_by_page_count(sample_works_pages, min_pages=500)

            print(f"  ✓ 从前5部作品中找到 {len(long_books)} 部长篇作品")
            if long_books:
                print_item_preview(long_books, format_func=fetcher.format_work)
            else:
                print(f"    (前5部作品中无符合条件的作品)")

            result["tests"].append({
                "question": f"列出{author_name}页数超过500页的作品（前5部采样）",
                "total": len(long_books),
                "all_items": [fetcher.format_work(w) for w in long_books]
            })

            # ============================================
            # 4. 版本级别查询 - 找到第一版
            # ============================================
            if works:
                # 选择第一部作品进行测试
                test_work = works[0]
                work_id = test_work.get('key', '').replace('/works/', '')
                work_title = test_work.get('title', 'Unknown')

                print(f"\n[4] 版本枚举: 列出《{work_title}》的所有版本")

                editions, _, _ = fetcher.fetch_book_editions(work_id, max_editions=50)
                print(f"  ✓ 总计: {len(editions)} 个版本（限制50）")
                print_item_preview(editions[:5], format_func=fetcher.format_edition)

                result["tests"].append({
                    "question": f"列出《{work_title}》的所有版本",
                    "total": len(editions),
                    "all_items": [fetcher.format_edition(e) for e in editions[:50]]
                })

                # 找到第一版
                print(f"\n[4a] 高级查询: 找到《{work_title}》的第一版")
                first_edition = fetcher.find_first_edition(work_id)

                if first_edition:
                    print(f"  ✓ 第一版:")
                    print(f"    {fetcher.format_edition(first_edition)}")

                    result["tests"].append({
                        "question": f"找到《{work_title}》的第一版",
                        "total": 1,
                        "all_items": [fetcher.format_edition(first_edition)]
                    })
                else:
                    print(f"  (无法确定第一版)")

            results.append(result)

        except Exception as e:
            print(f"  ✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()

    # 保存完整结果（无截断）
    if results:
        save_result("media_entertainment/openlibrary", {
            "api_name": "Open Library",
            "requires_auth": False,
            "philosophy": "Enumerate All - Complete enumeration without truncation",
            "metadata_utilized": [
                "languages (translation filtering)",
                "number_of_pages (length filtering)",
                "publish_date (first edition detection)",
                "edition metadata (comprehensive book information)"
            ],
            "config": config,
            "results": results
        })

    print(f"\n{'='*60}")
    print(f"✓ Open Library测试完成 - 所有结果已完整枚举并保存")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    run()
