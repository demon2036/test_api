# 列举全部 (Enumerate All) - AI搜索能力评估框架

## 🎯 核心理念

**AI搜索的本质不在于模糊推理，而在于"列举全部"（Enumerate All）的能力。**

- 完美的搜索系统不是最"聪明"的，而是最"完整"的
- 真正的智能搜索 = 枚举全集 + 判别过滤
- 模型的"困惑度"往往来自对全集的无知，而非任务本身的难度

## 📊 项目概览

这个框架提供了 **23 个真实API** 来评估AI系统的"列举全部"能力，覆盖 **6 个主要领域**：

| 领域 | API数量 | 示例 |
|------|---------|------|
| 代码生态系统 | 9 | NPM, PyPI, GitHub, Docker, Crates, RubyGems, NuGet, Go, Conda |
| 学术/科研 | 3 | arXiv, PubMed, USPTO Patents |
| 媒体/娱乐 | 4 | Spotify, YouTube, TMDb, Open Library |
| 知识/信息 | 1 | Wikipedia |
| 商业/金融 | 1 | SEC EDGAR |
| 基础设施/地理 | 2 | OpenStreetMap, crt.sh |

## 🚀 快速开始

### 1. 安装依赖
```bash
cd enumerate_framework
pip install requests
```

### 2. 运行测试
```bash
# 测试无需认证的新API
python test_new_apis.py

# 或者运行主程序生成完整测试集
python main.py
```

### 3. 查看结果
```bash
# 查看统计
python stats.py

# 验证API
python verify.py

# 查看生成的测试用例
cat output/test_cases.json
```

## 📖 核心文档

### 必读文档
- **[COMPLETION_REPORT.md](COMPLETION_REPORT.md)** - 完成报告，了解项目做了什么
- **[NEW_APIS_SUMMARY.md](NEW_APIS_SUMMARY.md)** - 新增API总结和理论意义
- **[API_CATALOG.md](API_CATALOG.md)** - 完整的API目录

### 技术文档
- **[enumerate_framework/docs/README.md](enumerate_framework/docs/README.md)** - 框架使用说明
- **[SUMMARY.md](SUMMARY.md)** - 项目重构总结

## 💡 测试原理

### "列举全部" → "稀疏问题" 转换

每个API可以生成两种等价的问题：

#### 1. 列举全部问题
```
问题: "列出作者 Yann LeCun 在arXiv上的所有论文标题"
答案: [论文1, 论文2, ..., 论文N]  ← 来自API
```

#### 2. Hash稀疏问题
```
问题: "在Yann LeCun的所有arXiv论文中，找出标题hash值为abc123的论文"
答案: 论文X  ← hash(论文X) == "abc123"
```

**核心洞察**: 如果模型能解出稀疏问题，说明它具备"等价枚举"能力！

### 为什么这很重要？

在信息完备的封闭世界中：
- "找到X" 和 "翻完所有牌找X" 在时间复杂度上是等价的
- 任何保证找到的过程，本质上都必须在潜在的全集上遍历
- **模型的"智能化"往往是用"模糊性"去掩盖"未列举"的问题**

## 🔬 实验设计优势

### 1. 真实API验证
- ✓ **客观性**: API返回的是确定的、可验证的完整集合
- ✓ **可重复性**: 任何人都可以调用相同的API验证结果
- ✓ **可扩展性**: 轻松添加新的测试用例

### 2. 多领域覆盖
不局限于代码领域，覆盖：
- 🔬 科学研究 (论文、专利)
- 🎬 娱乐媒体 (音乐、视频、电影、图书)
- 📚 知识信息 (维基百科)
- 💼 商业金融 (SEC文件)
- 🗺️ 地理信息 (地图、网络基础设施)

### 3. 无需大量标注
- 不需要人工标注"全集"
- 不需要模型生成参考答案
- 直接使用公开API的返回结果

## 📈 使用示例

### 示例1: 测试GitHub API

```python
from fetchers.github import GitHubFetcher

fetcher = GitHubFetcher()

# 列举全部问题
repos, api_info, question = fetcher.fetch_repos('torvalds')
print(f"问题: {question}")
print(f"仓库数量: {len(repos)}")
print(f"仓库列表: {repos}")

# 生成稀疏问题
import hashlib
target_hash = hashlib.md5(repos[5].encode()).hexdigest()[:6]
sparse_question = f"在torvalds的所有仓库中，找出仓库名hash值为{target_hash}的仓库"
print(f"稀疏问题: {sparse_question}")
print(f"答案: {repos[5]}")
```

### 示例2: 测试PubMed API

```python
from fetchers.pubmed import PubMedFetcher

fetcher = PubMedFetcher()

# 列举全部问题
pubs, api_info, question = fetcher.fetch_author_publications('Fauci AS', max_results=50)
print(f"问题: {question}")
print(f"论文数量: {len(pubs)}")

# 可以类似地生成稀疏问题
```

### 示例3: 测试crt.sh API

```python
from fetchers.crtsh import CrtShFetcher

fetcher = CrtShFetcher()

# 列举全部问题
certs, api_info, question = fetcher.fetch_domain_certificates('github.com')
print(f"问题: {question}")
print(f"证书/子域名数量: {len(certs)}")
```

## 🔧 添加新的API

### 1. 创建Fetcher类

```python
from .base import BaseFetcher
from typing import List, Dict, Tuple

class MyApiFetcher(BaseFetcher):
    def fetch(self, param: str) -> Tuple[List[str], Dict, str]:
        # 1. 构造API URL
        api_url = f"https://api.example.com/{param}"

        # 2. 实现分页逻辑（如果需要）
        results = []
        page = 1
        while True:
            response = requests.get(api_url, params={"page": page})
            data = response.json()
            if not data:
                break
            results.extend(data)
            page += 1

        # 3. 构造问题和API信息
        question = f"列出XXX的所有YYY"
        api_info = {
            "api_endpoint": api_url,
            "method": "GET",
            ...
        }

        return results, api_info, question

    def get_domain_name(self, **kwargs) -> str:
        return f"myapi_{kwargs.get('param')}"

    def get_metadata(self, **kwargs) -> Dict:
        return {"param": kwargs.get('param'), "platform": "MyAPI"}
```

### 2. 注册Fetcher

在 `fetchers/__init__.py` 中：
```python
from .myapi import MyApiFetcher

ALL_FETCHERS = [
    ...,
    MyApiFetcher,
]
```

## 📊 测试结果示例

```
✓ crt.sh: 找到 100 个证书/子域名 (github.com)
✓ Open Library: 找到 50 本书 (Isaac Asimov)
✓ SEC EDGAR: 找到 50 个文件 (Apple Inc.)
✓ PubMed: 找到 30 篇论文 (Fauci AS)
```

## 🎓 评估LLM

### 评估指标

1. **完整性 (Completeness)**
   - 模型是否枚举了所有结果？
   - 遗漏率是多少？

2. **准确性 (Accuracy)**
   - 枚举的结果是否正确？
   - 是否包含错误结果？

3. **诚实性 (Honesty)**
   - 模型是否承认无法完整枚举？
   - 还是"假装枚举"（给出部分结果但声称完整）？

4. **Hash解析能力**
   - 模型是否能解出稀疏问题？
   - 这间接证明了枚举能力

### 评估流程

```python
# 1. 生成测试集
test_cases = generate_test_cases()  # 200+ 用例

# 2. 查询LLM
for case in test_cases:
    llm_answer = query_llm(case.question)
    ground_truth = case.api_results

    # 3. 评估
    completeness = evaluate_completeness(llm_answer, ground_truth)
    accuracy = evaluate_accuracy(llm_answer, ground_truth)

    # 4. Hash测试
    if case.type == "sparse":
        hash_solved = (llm_answer == case.hash_target)
```

## 📈 预期研究成果

### 可能的发现

1. **枚举盲区**: 模型在哪些领域无法完整枚举？
   - 代码包版本 vs 学术论文
   - 结构化数据 vs 非结构化数据

2. **假装枚举**: 模型是否会给出部分结果但声称完整？

3. **领域差异**: 不同领域的枚举能力是否有显著差异？

4. **规模效应**: 模型大小与枚举能力的关系？

### 潜在论文

**标题**: "Beyond Fuzzy Search: Evaluating Complete Enumeration Capabilities of Large Language Models"

**贡献**:
- 提出"列举全部"作为AI搜索能力的核心指标
- 构建跨领域、可验证的评估框架（23个API, 6个领域）
- 揭示现有LLM的"枚举盲区"
- 证明Hash测试与完整枚举的等价性

## 📝 项目结构

```
enumerate_framework/
├── core/              # 核心模块
│   ├── generator.py   # 测试用例生成器
│   └── hasher.py      # Hash计算
├── fetchers/          # API获取器 (23个)
│   ├── npm.py         # JavaScript/NPM
│   ├── pypi.py        # Python
│   ├── github.py      # Git仓库
│   ├── arxiv.py       # 学术论文
│   ├── pubmed.py      # 生物医学论文
│   ├── spotify.py     # 音乐
│   ├── youtube.py     # 视频
│   ├── wikipedia.py   # 百科
│   ├── sec_edgar.py   # 金融
│   ├── crtsh.py       # 证书
│   └── ...
├── main.py            # 主程序
├── stats.py           # 统计
├── verify.py          # 验证
├── test_new_apis.py   # 测试脚本
└── output/            # 输出结果
```

## 🤝 贡献

欢迎贡献新的API fetcher！

要求：
1. 必须支持完整枚举（分页或一次性返回）
2. 必须使用真实的公开API
3. 必须提供清晰的API文档信息
4. 必须实现 BaseFetcher 接口

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有提供公开API的平台：
- NPM, PyPI, GitHub, Docker Hub, Crates.io, RubyGems, NuGet, Go Proxy, Conda
- arXiv, PubMed, USPTO
- Spotify, YouTube, TMDb, Open Library
- Wikipedia
- SEC EDGAR
- OpenStreetMap, crt.sh

---

**核心洞察**: 搜索的智能化本质上是用"模糊性"去掩盖"未列举"的问题。这个框架帮助我们量化评估AI系统的"列举全部"能力。
