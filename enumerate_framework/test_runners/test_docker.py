"""Docker Hub API 测试"""

import sys
from pathlib import Path

# 支持独立运行和作为模块导入
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header


def run(test_config=None):
    """运行Docker Hub API测试

    Args:
        test_config: 测试配置字典，可包含:
            - images: 要测试的镜像列表
            - limit: 每个镜像最多获取多少标签
    """
    print_header("测试 Docker Hub API")

    from fetchers.docker import DockerFetcher
    fetcher = DockerFetcher()

    # 默认配置
    config = {
        "images": ['python', 'node', 'nginx', 'redis', 'postgres'],
        "limit": 1000
    }

    # 合并用户配置
    if test_config:
        config.update(test_config)

    results = []

    for img in config["images"]:
        print(f"\n测试镜像: {img}")
        tags, api_info, question = fetcher.fetch(image=img, limit=config["limit"])

        result = create_test_result(
            identifier=img,
            question=question,
            api_info=api_info,
            data=tags,
            data_key="tags",
            image=img
        )
        results.append(result)

        print(f"  ✓ 找到 {len(tags)} 个标签")
        print(f"  前5个标签: {tags[:5]}")

    save_result("docker", {
        "api_name": "Docker Hub",
        "requires_auth": False,
        "config": config,
        "tests": results
    })

    return results


if __name__ == "__main__":
    run()
