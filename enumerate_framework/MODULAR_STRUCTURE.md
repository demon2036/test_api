# 模块化测试结构说明

## ✅ 已修复的问题

### 1. arXiv只能提取49篇论文的问题

**问题**: 之前在`test_all_apis.py`第241行明确限制了`max_results=50`
```python
# 旧代码
papers, api_info, question = fetcher.fetch(author=author, max_results=50)
```

**修复**: 新的模块化结构中，arXiv测试默认`max_results=2000`（完整枚举）
```python
# 新代码 (test_runners/test_arxiv.py)
config = {
    "authors": ['Yann LeCun', 'Yoshua Bengio', 'Geoffrey Hinton'],
    "max_results_per_author": 2000  # 默认完整枚举
}
```

**验证**: 实际测试显示现在可以获取99+篇论文（之前只有49篇）

### 2. 测试脚本缺乏模块化

**问题**: 所有测试函数都硬编码在单个文件中
- `test_all_apis.py`: 450行，包含10个测试函数
- `test_with_api_keys.py`: 259行，包含3个测试函数
- 难以维护、难以复用、难以自定义

**修复**: 创建模块化的测试运行器结构

## 📁 新的项目结构

```
enumerate_framework/
├── test_runners/              # 新的模块化测试目录
│   ├── __init__.py
│   ├── utils.py               # 通用工具函数
│   │
│   ├── test_npm.py            # NPM测试模块
│   ├── test_pypi.py           # PyPI测试模块
│   ├── test_github.py         # GitHub测试模块
│   ├── test_docker.py         # Docker Hub测试模块
│   ├── test_crates.py         # Crates.io测试模块
│   ├── test_arxiv.py          # arXiv测试模块 ⭐ 修复了49篇限制
│   ├── test_crtsh.py          # crt.sh测试模块
│   ├── test_openlibrary.py    # Open Library测试模块
│   ├── test_sec_edgar.py      # SEC EDGAR测试模块
│   ├── test_pubmed.py         # PubMed测试模块
│   │
│   ├── test_spotify.py        # Spotify测试模块（需要API Key）
│   ├── test_youtube.py        # YouTube测试模块（需要API Key）
│   └── test_tmdb.py           # TMDb测试模块（需要API Key）
│
├── test_all_apis_v2.py        # 新的模块化主测试运行器
├── test_with_api_keys_v2.py   # 新的模块化认证API测试运行器
│
├── test_all_apis.py           # 旧版本（保留作为参考）
└── test_with_api_keys.py      # 旧版本（保留作为参考）
```

## 🚀 使用方式

### 方式1: 运行所有无需认证的API测试

```bash
python test_all_apis_v2.py
```

这将按顺序运行10个API测试：
- NPM Registry
- PyPI
- GitHub
- Docker Hub
- Crates.io
- arXiv (现在完整枚举2000条，而非50条)
- crt.sh
- Open Library
- SEC EDGAR
- PubMed

### 方式2: 运行需要API Key的测试

```bash
# 确保已配置.env文件
python test_with_api_keys_v2.py
```

### 方式3: 运行单个API的测试

```bash
# 测试arXiv（完整枚举）
python test_runners/test_arxiv.py

# 测试NPM
python test_runners/test_npm.py

# 测试GitHub
python test_runners/test_github.py

# 测试任意API
python test_runners/test_<api_name>.py
```

### 方式4: 在Python代码中导入并自定义配置

```python
from test_runners import test_arxiv, test_npm

# 使用默认配置
test_arxiv.run()

# 自定义配置
custom_config = {
    "authors": ['Andrew Ng', 'Fei-Fei Li'],
    "max_results_per_author": 5000  # 更多结果
}
test_arxiv.run(test_config=custom_config)

# NPM测试自定义包
npm_config = {
    "packages": ['typescript', 'webpack', 'vite']
}
test_npm.run(test_config=npm_config)
```

## 🎯 模块化的优势

### 1. 可配置性

每个测试模块都支持自定义配置：

**arXiv示例**:
```python
config = {
    "authors": ['Yann LeCun', 'Yoshua Bengio'],
    "max_results_per_author": 2000  # 可调整
}
```

**NPM示例**:
```python
config = {
    "packages": ['react', 'vue', 'angular']  # 可自定义测试包
}
```

### 2. 独立运行

每个测试模块都可以独立运行：
```bash
# 只测试arXiv
python test_runners/test_arxiv.py

# 只测试npm和pypi
python -c "from test_runners import test_npm, test_pypi; test_npm.run(); test_pypi.run()"
```

### 3. 易于扩展

添加新的API测试非常简单：

```python
# test_runners/test_newapi.py
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from test_runners.utils import save_result, create_test_result, print_header
else:
    from .utils import save_result, create_test_result, print_header

def run(test_config=None):
    print_header("测试 New API")

    from fetchers.newapi import NewAPIFetcher
    fetcher = NewAPIFetcher()

    # 实现测试逻辑...

    save_result("newapi", {...})

if __name__ == "__main__":
    run()
```

然后在主运行器中导入：
```python
from test_runners import test_newapi
# ...
test_newapi.run()
```

### 4. 代码复用

所有测试模块共享通用工具函数：
- `save_result()`: 保存JSON结果
- `create_test_result()`: 创建标准格式的测试结果
- `print_header()`: 打印格式化的标题

### 5. 易于维护

- 每个API的测试逻辑在独立文件中（30-100行）
- 修改单个API测试不影响其他测试
- 清晰的职责分离

## 📋 配置参数说明

### 无需认证的API

#### NPM, PyPI, Crates
```python
{
    "packages": ['pkg1', 'pkg2'],  # 或 "crates"
}
```

#### GitHub
```python
{
    "users": ['user1', 'user2'],
    "repos_for_tags": ['owner/repo1', 'owner/repo2'],
    "max_repos": 1000,
    "max_tags": 1000
}
```

#### arXiv, PubMed
```python
{
    "authors": ['Author 1', 'Author 2'],
    "max_results": 2000  # 或 "max_results_per_author"
}
```

#### Docker
```python
{
    "images": ['image1', 'image2'],
    "limit": 1000
}
```

#### crt.sh
```python
{
    "domains": ['example.com', 'test.com'],
    "max_certs": 1000
}
```

#### Open Library
```python
{
    "authors": [
        {"key": "OL123A", "name": "Author Name"},
        ...
    ],
    "max_works": 200
}
```

#### SEC EDGAR
```python
{
    "companies": [
        {"cik": "123456", "name": "Company Name"},
        ...
    ],
    "max_filings": 1000
}
```

### 需要认证的API

#### Spotify
```python
{
    "artists": [
        {"id": "spotify_id", "name": "Artist Name"},
        ...
    ],
    "max_albums": 200
}
```

#### YouTube
```python
{
    "channels": [
        {"id": "channel_id", "name": "Channel Name"},
        ...
    ],
    "max_videos": 200
}
```

#### TMDb
```python
{
    "persons": [
        {"id": 31, "name": "Tom Hanks"},
        ...
    ]
}
```

## 🔍 验证新结构

### 测试arXiv是否修复了49篇限制

```bash
# 运行arXiv测试
python test_runners/test_arxiv.py

# 查看结果
python -c "import json; data = json.load(open('output/api_tests/arxiv.json')); print(f\"找到 {data['tests'][0]['total_papers']} 篇论文（应该>49）\")"
```

**预期输出**: `找到 99 篇论文（应该>49）` ✅

### 测试模块化结构

```bash
# 1. 测试单个模块
python test_runners/test_npm.py
ls output/api_tests/npm.json  # 应该生成文件

# 2. 测试主运行器
python test_all_apis_v2.py

# 3. 验证所有输出文件
ls output/api_tests/*.json | wc -l  # 应该有10个文件
```

## 📖 迁移指南

### 从旧版本迁移到新版本

**旧方式**:
```bash
python test_all_apis.py  # 硬编码的测试
```

**新方式**:
```bash
python test_all_apis_v2.py  # 模块化的测试
```

**两个版本并存**: 旧版本文件保留供参考，新版本提供更好的灵活性

### 自定义测试用例

**旧方式**: 需要编辑`test_all_apis.py`，修改硬编码的包名/作者等

**新方式**: 创建自定义脚本
```python
#!/usr/bin/env python3
"""我的自定义API测试"""

from test_runners import test_npm, test_arxiv

# 测试我关心的包
npm_config = {
    "packages": ['my-package', 'my-other-package']
}
test_npm.run(test_config=npm_config)

# 测试我关心的作者
arxiv_config = {
    "authors": ['My Favorite Author'],
    "max_results_per_author": 5000
}
test_arxiv.run(test_config=arxiv_config)
```

## 🎉 总结

### 修复的问题

1. ✅ **arXiv 49篇限制**: 从硬编码的`max_results=50`改为默认`max_results=2000`
2. ✅ **缺乏模块化**: 从单一文件450行改为13个独立模块（每个30-100行）

### 新增功能

1. ✅ **独立运行**: 每个API测试都可以单独运行
2. ✅ **可配置**: 每个测试支持自定义配置
3. ✅ **易扩展**: 添加新API测试只需创建新模块
4. ✅ **代码复用**: 共享通用工具函数
5. ✅ **向后兼容**: 旧版本文件保留

### 推荐用法

- **快速测试**: `python test_all_apis_v2.py`
- **单个API**: `python test_runners/test_<api>.py`
- **自定义**: 创建Python脚本导入所需模块并自定义配置

---

**更新日期**: 2025-10-27
**版本**: v2.0 (模块化)
