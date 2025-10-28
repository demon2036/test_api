# AI列举能力测试框架 v2.0

## 🎯 项目简介

测试AI系统的"列举全部"能力，而非传统的模糊匹配能力。

**核心理念**：
> 真正的智能不在于模糊地猜测，而在于完整地枚举。

## 📁 项目结构

```
enumerate_framework/
├── core/              # 核心模块
│   ├── generator.py   # 测试生成器
│   └── hasher.py      # Hash计算
├── fetchers/          # API获取器
│   ├── npm.py         # NPM包
│   ├── pypi.py        # PyPI包
│   ├── github.py      # GitHub数据
│   ├── docker.py      # Docker镜像
│   ├── crates.py      # Rust Crates
│   ├── rubygems.py    # Ruby Gems
│   ├── nuget.py       # NuGet包
│   ├── go_proxy.py    # Go模块
│   ├── arxiv.py       # arXiv论文
│   └── conda.py       # Conda包
├── main.py            # 主程序
├── stats.py           # 统计报告
├── verify.py          # API验证
├── docs/              # 文档
└── output/            # 输出数据

test_cases.json        # 生成的测试数据
```

## 🚀 快速使用

### 1. 生成测试数据

```bash
cd enumerate_framework
python main.py
```

生成的数据保存在 `output/test_cases.json`

### 2. 查看统计

```bash
python stats.py
```

### 3. 验证API

```bash
python verify.py
```

## 📊 数据集规模

- **21个测试域**
- **5,000+可枚举项目**
- **100+稀疏查找问题**
- **10个不同的API生态系统**

## 🎯 核心特性

### 1. 模块化设计
每个API一个独立的fetcher模块，代码清晰易维护。

### 2. 完整的API信息
每个测试域记录完整的API调用信息，任何人都可以验证。

### 3. 真实数据
所有数据通过API获取，AI无法靠记忆回答。

## 📖 使用示例

### 添加新的API源

创建新的fetcher文件 `fetchers/your_api.py`:

```python
from .base import BaseFetcher

class YourAPIFetcher(BaseFetcher):
    def fetch(self, **kwargs):
        # 实现API调用
        items = []  # 获取数据
        api_info = {}  # API信息
        question = ""  # 问题描述
        return items, api_info, question

    def get_domain_name(self, **kwargs):
        return "your_domain"

    def get_metadata(self, **kwargs):
        return {}
```

在 `main.py` 中使用:

```python
from fetchers.your_api import YourAPIFetcher

fetcher = YourAPIFetcher()
items, api_info, question = fetcher.fetch()
generator.add_test_case(...)
```

## 🔬 测试原理

### 列举问题
```
Q: 列出Python requests库在PyPI上的所有发布版本号
A: [0.0.1, 0.10.0, ..., 2.32.5]
```

### 稀疏Hash查找
```
Q: 找到SHA256哈希值前8位为 6b13789e 的版本
A: 0.0.1
```

**关键**：如果AI能答对稀疏问题，说明它必然枚举了全部！

## 📝 API调用信息

每个测试域包含:
- `api_endpoint` - API URL
- `method` - HTTP方法
- `parameters` - 查询参数
- `authentication` - 认证方式
- `rate_limit` - 速率限制
- `documentation` - 官方文档

完全可验证！

## 🌟 数据来源

- **NPM** (JavaScript)
- **PyPI** (Python)
- **Crates.io** (Rust)
- **RubyGems** (Ruby)
- **NuGet** (.NET)
- **Go Proxy** (Go)
- **Docker Hub**
- **GitHub**
- **arXiv** (学术)
- **Conda**

---

**版本**: v2.0
**文档**: `docs/API_GUIDE.md`
