"""模块化的API测试运行器"""

# 代码生态系统相关测试
from .code_ecosystem import (
    test_npm,
    test_pypi,
    test_github,
    test_github_forked_repos,
    test_github_new_features,
    test_crates,
    test_rubygems,
    test_nuget,
    test_go_proxy,
    test_conda,
    test_cran,
    test_homebrew,
)

# 学术/科研相关测试
from .academic_research import (
    test_dblp,
    test_dblp_enhanced,
    test_pubmed,
    test_pubmed_enhanced,
    test_zenodo,
    test_zenodo_enhanced,
)

# AI/ML相关测试
from .ai_ml import test_huggingface

# 媒体/娱乐相关测试
from .media_entertainment import (
    test_spotify,
    test_youtube,
    test_tmdb,
    test_openlibrary,
)

# 政府/开放数据相关测试
from .government_opendata import test_datagov
