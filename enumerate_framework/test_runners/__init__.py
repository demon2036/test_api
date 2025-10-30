"""模块化的API测试运行器"""

# 代码生态系统相关测试
from .code_ecosystem import (
    test_npm,
    test_pypi,
    test_github,
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
    dblp,
    run_pubmed as pubmed,  # deprecated, kept for backward compatibility
    run_zenodo as zenodo,  # deprecated, kept for backward compatibility
)

# AI/ML相关测试
from .ai_ml import test_huggingface

# 媒体/娱乐相关测试
from .media_entertainment import (
    test_spotify,
    test_youtube,
    test_tmdb,
)

# 政府/开放数据相关测试
from .government_opendata import test_datagov
