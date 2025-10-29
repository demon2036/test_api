"""GitHub API Fetcher"""

import requests
import time
from typing import List, Dict, Tuple, Callable, Any, Optional
from datetime import datetime, timedelta
from ..base import BaseFetcher


class GitHubFetcher(BaseFetcher):
    """GitHub数据获取器 - 精简版"""

    def _paginated_fetch(self, url: str, params: Dict, max_items: int,
                         extractor: Callable[[Dict], Any], error_context: str) -> List[Any]:
        """通用分页获取逻辑"""
        items = []
        page = 1
        try:
            while len(items) < max_items:
                response = requests.get(url, params={**params, "per_page": 100, "page": page}, timeout=10)
                if response.status_code != 200:
                    break
                data = response.json()
                if not data:
                    break
                items.extend([extractor(item) for item in data])
                page += 1
                time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ GitHub API错误 ({error_context}): {e}")
        return items[:max_items]

    def fetch_repos(self, username: str, max_repos: int = 100) -> Tuple[List[str], Dict, str]:
        """获取用户的所有仓库"""
        api_url = f"https://api.github.com/users/{username}/repos"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"per_page": 100, "sort": "updated"},
            "authentication": "Optional (Bearer token for higher rate limits)",
            "rate_limit": "60/hour (unauth), 5000/hour (auth)",
            "documentation": "https://docs.github.com/en/rest/repos/repos#list-repositories-for-a-user"
        }

        repos = self._paginated_fetch(api_url, {"sort": "updated"}, max_repos,
                                      lambda r: r['full_name'], f"repos/{username}")
        question = f"列出GitHub用户{username}的所有公开仓库"
        return repos, api_info, question

    def fetch_tags(self, repo: str, max_tags: int = 1000) -> Tuple[List[str], Dict, str]:
        """获取仓库的所有tags"""
        api_url = f"https://api.github.com/repos/{repo}/tags"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"per_page": 100},
            "documentation": "https://docs.github.com/en/rest/repos/repos#list-repository-tags"
        }

        tags = self._paginated_fetch(api_url, {}, max_tags, lambda t: t['name'], f"tags/{repo}")
        question = f"列出{repo}仓库的所有版本标签(tags)"
        return tags, api_info, question

    def fetch_releases(self, repo: str, max_releases: int = 1000,
                      include_metadata: bool = False) -> Tuple[List, Dict, str]:
        """获取仓库的所有releases，可选返回元数据"""
        api_url = f"https://api.github.com/repos/{repo}/releases"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"per_page": 100},
            "documentation": "https://docs.github.com/en/rest/releases/releases#list-releases"
        }

        if include_metadata:
            extractor = lambda r: {
                "tag_name": r['tag_name'],
                "name": r['name'],
                "prerelease": r['prerelease'],
                "published_at": r['published_at']
            }
        else:
            extractor = lambda r: f"{r['tag_name']} - {r['name']}"

        releases = self._paginated_fetch(api_url, {}, max_releases, extractor, f"releases/{repo}")
        question = f"列出{repo}仓库的所有releases"
        return releases, api_info, question

    def fetch_branches(self, repo: str, max_branches: int = 1000,
                       include_metadata: bool = False) -> Tuple[List, Dict, str]:
        """获取仓库的所有分支，可选返回元数据"""
        api_url = f"https://api.github.com/repos/{repo}/branches"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"per_page": 100},
            "documentation": "https://docs.github.com/en/rest/branches/branches#list-branches"
        }

        if include_metadata:
            # 需要额外API调用获取完整分支信息
            branches = []
            simple_branches = self._paginated_fetch(api_url, {}, max_branches,
                                                   lambda b: b['name'], f"branches/{repo}")
            for branch_name in simple_branches:
                try:
                    detail_url = f"{api_url}/{branch_name}"
                    response = requests.get(detail_url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        branches.append({
                            "name": branch_name,
                            "last_commit_date": data['commit']['commit']['committer']['date']
                        })
                    time.sleep(0.5)
                except Exception as e:
                    print(f"  ✗ 获取分支{branch_name}详情失败: {e}")
            return branches[:max_branches], api_info, f"列出{repo}仓库的所有分支及元数据"
        else:
            branches = self._paginated_fetch(api_url, {}, max_branches,
                                           lambda b: b['name'], f"branches/{repo}")

        question = f"列出{repo}仓库的所有分支"
        return branches, api_info, question

    def fetch_forked_repos(self, username: str, max_repos: int = 100) -> Tuple[List[str], Dict, str]:
        """获取用户的所有forked仓库 - TODO已实现"""
        api_url = f"https://api.github.com/users/{username}/repos"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"per_page": 100, "type": "forks"},
            "documentation": "https://docs.github.com/en/rest/repos/repos#list-repositories-for-a-user"
        }

        repos = self._paginated_fetch(api_url, {"type": "forks"}, max_repos,
                                      lambda r: r['full_name'], f"forked_repos/{username}")
        question = f"列出GitHub用户{username}的所有forked仓库"
        return repos, api_info, question

    def fetch_repos_with_metadata(self, username: str, max_repos: int = 100) -> Tuple[List[Dict], Dict, str]:
        """获取用户的所有仓库及元数据（stars, language, fork, created_at）"""
        api_url = f"https://api.github.com/users/{username}/repos"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            "parameters": {"per_page": 100, "sort": "updated"},
            "documentation": "https://docs.github.com/en/rest/repos/repos#list-repositories-for-a-user"
        }

        repos = self._paginated_fetch(
            api_url, {"sort": "updated"}, max_repos,
            lambda r: {
                "name": r['full_name'],
                "stars": r['stargazers_count'],
                "forks": r['forks_count'],  # 被fork的次数
                "language": r.get('language'),
                "is_fork": r['fork'],
                "created_at": r['created_at']
            },
            f"repos_metadata/{username}"
        )
        question = f"列出GitHub用户{username}的所有公开仓库及元数据"
        return repos, api_info, question

    # ========== 过滤器 - 实现GEMINI.md中的TODO功能 ==========

    def filter_prerelease(self, releases: List[Dict]) -> List[Dict]:
        """过滤出pre-release版本 - TODO已实现"""
        return [r for r in releases if r.get('prerelease', False)]

    def filter_stale_branches(self, branches: List[Dict], months: int = 12) -> List[Dict]:
        """过滤出超过指定月份未更新的分支 - TODO已实现"""
        from datetime import timezone
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=months * 30)
        stale = []
        for branch in branches:
            last_commit_str = branch.get('last_commit_date')
            if last_commit_str:
                try:
                    last_commit = datetime.fromisoformat(last_commit_str.replace('Z', '+00:00'))
                    if last_commit < cutoff_date:
                        stale.append(branch)
                except ValueError:
                    pass
        return stale

    def get_most_starred_repo(self, repos: List[Dict]) -> Optional[Dict]:
        """找出star数最多的仓库 - TODO已实现"""
        if not repos:
            return None
        return max(repos, key=lambda r: r.get('stars', 0))

    def filter_by_stars(self, repos: List[Dict], min_stars: int) -> List[Dict]:
        """根据star数量过滤仓库"""
        return [r for r in repos if r.get('stars', 0) > min_stars]

    def filter_by_forks(self, repos: List[Dict], min_forks: int) -> List[Dict]:
        """根据被fork次数过滤仓库"""
        return [r for r in repos if r.get('forks', 0) > min_forks]

    def filter_by_language(self, repos: List[Dict], language: str) -> List[Dict]:
        """根据主编程语言过滤仓库"""
        return [r for r in repos if r.get('language') == language]

    def filter_by_fork_status(self, repos: List[Dict], is_fork: bool) -> List[Dict]:
        """根据是否为fork过滤仓库"""
        return [r for r in repos if r.get('is_fork', False) == is_fork]

    def filter_by_created_date(self, repos: List[Dict], min_year: int) -> List[Dict]:
        """根据创建日期过滤仓库 (晚于指定年份)"""
        filtered_repos = []
        for repo in repos:
            created_at_str = repo.get('created_at')
            if created_at_str:
                try:
                    created_year = int(created_at_str[:4])
                    if created_year > min_year:
                        filtered_repos.append(repo)
                except (ValueError, IndexError):
                    pass
        return filtered_repos

    # ========== BaseFetcher抽象方法实现 ==========

    def fetch(self, **kwargs) -> Tuple[List, Dict, str]:
        """默认fetch实现，支持多种类型"""
        fetch_type = kwargs.get('fetch_type', 'repos')
        if fetch_type == 'forked_repos':
            return self.fetch_forked_repos(kwargs.get('username', 'torvalds'))
        elif fetch_type == 'repos_metadata':
            return self.fetch_repos_with_metadata(kwargs.get('username', 'torvalds'))
        return self.fetch_repos(kwargs.get('username', 'torvalds'))

    def get_domain_name(self, **kwargs) -> str:
        return f"github_{kwargs.get('username', 'user')}_{kwargs.get('fetch_type', 'repos')}"

    def get_metadata(self, **kwargs) -> Dict:
        return {
            "username": kwargs.get('username', ''),
            "platform": "GitHub",
            "fetch_type": kwargs.get('fetch_type', 'repos')
        }
