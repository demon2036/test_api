# 列举全部 (Enumerate All) - API测试框架

## ⚡ 新版本：模块化测试结构 (v2.0)

**重要更新**:
- ✅ 修复了arXiv只能提取49篇论文的问题（现在支持完整枚举2000+）
- ✅ 重构为模块化结构，每个API独立测试模块
- ✅ 支持自定义配置和独立运行
- 📖 详细文档见 [MODULAR_STRUCTURE.md](MODULAR_STRUCTURE.md)

### 推荐使用新版本

```bash
# 新版本：模块化测试运行器
python test_all_apis_v2.py        # 所有无需认证的API
python test_with_api_keys_v2.py   # 需要API Key的服务

# 独立运行单个API测试
python test_runners/test_arxiv.py
python test_runners/test_npm.py
```

**旧版本** (`test_all_apis.py`) 仍然保留供参考使用。

---

## 🚀 快速开始

### 1. 测试无需认证的API（推荐先运行）

这些API可以直接测试，无需任何配置：

```bash
cd enumerate_framework

# 推荐：使用新的模块化版本
python test_all_apis_v2.py

# 或使用旧版本
python test_all_apis.py
```

**测试的API** (总计25个，100%精确):
- ✓ NPM Registry (JavaScript包)
- ✓ PyPI (Python包)
- ✓ GitHub (代码仓库)
- ✓ Docker Hub (容器镜像)
- ✓ Crates.io (Rust包)
- ✓ **CRAN** (R包) ⭐ 新增
- ✓ **Maven Central** (Java/JVM包) ⭐ 新增
- ✓ **Homebrew** (macOS/Linux包) ⭐ 新增
- ✓ **DBLP** (计算机科学论文 - 使用PID精确标识符) ⭐
- ✓ **crt.sh** (SSL证书透明度日志 - 用于安全研究和子域名发现)
- ✓ Open Library (图书)
- ✓ **SEC EDGAR** (美国证券交易委员会公司文件 - 使用CIK唯一标识符)
- ✓ **PubMed** (生物医学论文 - 支持ORCID) ⭐
- ✓ **Zenodo** (研究数据仓库 - 使用ORCID/DOI) ⭐ 新增

**已删除的不精确API**:
- ✗ arXiv - 作者名字搜索不精确（已用DBLP替换）
- ✗ USPTO - 发明人名字搜索不精确
- ✗ OpenStreetMap - 社区数据完整性无保证

详见 [API_QUALITY_CRITERIA.md](../API_QUALITY_CRITERIA.md)

**输出位置**: `output/api_tests/*.json`

每个API的测试结果保存在独立的JSON文件中。

### 2. 查看测试结果

```bash
# 查看所有生成的输出文件
ls -lh output/api_tests/

# 查看NPM测试结果
cat output/api_tests/npm.json | python -m json.tool | less

# 查看所有结果的摘要
python stats.py
```

### 3. 测试需要API Key的服务（可选）

#### 步骤1: 安装python-dotenv

```bash
pip install python-dotenv
```

#### 步骤2: 配置API凭据

```bash
# 复制.env示例文件
cp .env.example .env

# 编辑.env文件，填入你的API凭据
nano .env  # 或使用其他编辑器
```

#### 步骤3: 获取API凭据

| 服务 | 获取地址 | 需要的变量 |
|------|---------|-----------|
| **Spotify** | https://developer.spotify.com/dashboard | `SPOTIFY_CLIENT_ID`<br>`SPOTIFY_CLIENT_SECRET` |
| **YouTube** | https://console.cloud.google.com/apis/credentials | `YOUTUBE_API_KEY` |
| **TMDb** | https://www.themoviedb.org/settings/api | `TMDB_API_KEY` |

#### 步骤4: 运行测试

```bash
python test_with_api_keys.py
```

这个脚本会：
- ✓ 检查哪些API凭据已配置
- ✓ 只测试已配置的服务
- ✓ 跳过未配置的服务（并给出提示）
- ✓ 将结果保存到 `output/api_tests/` 目录

## 📊 输出文件格式

每个API的输出文件包含：

```json
{
  "api_name": "NPM Registry",
  "requires_auth": false,
  "tests": [
    {
      "package": "react",
      "question": "列出NPM上react包的所有发布版本号",
      "api_info": {
        "api_endpoint": "https://registry.npmjs.org/react",
        "method": "GET",
        "parameters": {},
        "authentication": "None",
        "rate_limit": "No official limit",
        "documentation": "https://github.com/npm/registry/blob/master/docs/REGISTRY-API.md"
      },
      "total_versions": 2573,
      "sample_versions": ["0.0.1", "0.0.2", ...],
      "all_versions": [...],  // 完整的版本列表
      "timestamp": "2025-10-27T..."
    }
  ]
}
```

## 📁 项目结构

```
enumerate_framework/
├── .env.example          # API凭据配置模板
├── .env                  # 你的API凭据（需自己创建）
├── README.md             # 本文件
├── test_all_apis.py      # 测试无需认证的API ⭐
├── test_with_api_keys.py # 测试需要API Key的服务
├── main.py               # 生成完整测试集
├── stats.py              # 统计分析
├── verify.py             # 验证API
├── output/
│   └── api_tests/        # 每个API的测试输出
│       ├── npm.json
│       ├── pypi.json
│       ├── github.json
│       └── ...
└── fetchers/             # API获取器
    ├── npm.py
    ├── pypi.py
    ├── github.py
    └── ...
```

## 🔍 可用的API清单

### 无需认证 (18个) ✓

| API | 枚举内容 | 文件位置 |
|-----|---------|---------|
| **代码生态系统 (12个)** |||
| NPM | 包的所有版本 | `fetchers/npm.py` |
| PyPI | 包的所有版本 | `fetchers/pypi.py` |
| GitHub | 仓库、tags、releases、branches | `fetchers/github.py` |
| Docker Hub | 镜像的所有标签 | `fetchers/docker.py` |
| Crates.io | crate的所有版本 | `fetchers/crates.py` |
| RubyGems | gem的所有版本 | `fetchers/rubygems.py` |
| NuGet | 包的所有版本 | `fetchers/nuget.py` |
| Go Proxy | 模块的所有版本 | `fetchers/go_proxy.py` |
| Conda | 包的所有版本 | `fetchers/conda.py` |
| CRAN | R包的所有版本 | `fetchers/cran.py` |
| Maven Central | Java包的所有版本 | `fetchers/maven.py` |
| Homebrew | Formula的当前版本 | `fetchers/homebrew.py` |
| **学术/科研 (3个)** |||
| DBLP | 作者的所有论文（使用PID） | `fetchers/dblp.py` |
| PubMed | 作者的所有出版物（支持ORCID） | `fetchers/pubmed.py` |
| Zenodo | 研究者的所有数据（使用ORCID） | `fetchers/zenodo.py` |
| **其他 (3个)** |||
| Open Library | 作者的所有作品 | `fetchers/goodreads.py` |
| SEC EDGAR | 公司的所有文件（使用CIK） | `fetchers/sec_edgar.py` |
| crt.sh | 域名的所有SSL证书 | `fetchers/crtsh.py` |
| Wikipedia | 分类页面、修订历史 | `fetchers/wikipedia.py` |

### 需要API Key (4个)

| API | 枚举内容 | 认证类型 | 文件位置 |
|-----|---------|---------|---------|
| Spotify | 艺术家的所有专辑 | OAuth 2.0 | `fetchers/spotify.py` |
| YouTube | 频道的所有视频 | API Key | `fetchers/youtube.py` |
| TMDb | 演员的所有作品 | API Key | `fetchers/tmdb.py` |
| IMDb/OMDb | 电影搜索 | API Key | `fetchers/imdb.py` |

### 📚 重要API说明

#### SEC EDGAR - 美国证券交易委员会文件数据库

**什么是SEC EDGAR？**
- **SEC** = U.S. Securities and Exchange Commission（美国证券交易委员会）
- **EDGAR** = Electronic Data Gathering, Analysis, and Retrieval（电子数据收集、分析和检索系统）
- 所有美国上市公司必须向SEC提交财务报告和重要文件

**为什么精确？**
- 使用 **CIK (Central Index Key)** - 10位数字的唯一公司标识符
- 例如：Apple Inc. = CIK `0000320193`，Tesla = CIK `0001318605`

**枚举什么？**
- **10-K**: 年度报告（完整财务状况）
- **10-Q**: 季度报告
- **8-K**: 重大事件报告（收购、高管变动等）
- 其他：招股说明书、代理声明等

**用例示例：**
```python
# 列出Apple公司的所有SEC文件
fetcher.fetch_company_filings(cik="320193")
```

#### crt.sh - SSL证书透明度日志

**什么是crt.sh？**
- **证书透明度(Certificate Transparency)** 的公开搜索引擎
- 记录所有已颁发的SSL/TLS证书（公开、不可篡改）

**为什么精确？**
- 证书颁发必须记录到CT日志（强制性要求）
- 使用域名作为唯一标识符
- 完整枚举一个域名的所有证书和子域名

**枚举什么？**
- 主域名的所有SSL证书
- 发现所有子域名（例如：`api.example.com`, `mail.example.com`）
- 证书的颁发者、有效期等

**用例示例：**
```python
# 列出google.com的所有证书和子域名
fetcher.fetch_domain_certificates(domain="google.com")
# 结果：google.com, www.google.com, mail.google.com, drive.google.com...
```

**安全研究价值：**
- 子域名发现（渗透测试、资产盘点）
- 证书历史追踪
- 检测未授权的证书颁发

## ⚠️ 重要说明

### 关于分页

所有API都已正确实现了完整枚举：
- ✓ **支持分页的API**: 正确实现了分页循环
- ✓ **一次性返回的API**: 直接获取完整数据集

### 关于速率限制

某些API有速率限制：
- **PubMed**: 3请求/秒 (无key), 10请求/秒 (有key)
- **arXiv**: 建议3秒/请求
- **Crates.io**: 建议1请求/秒
- **GitHub**: 60请求/小时 (无认证)
- **YouTube**: 10,000 quota units/天
- **TMDb**: 40请求/10秒

测试脚本已经内置了适当的延迟来遵守这些限制。

## 🐛 故障排查

### 问题: test_all_apis.py 运行失败

**解决方案**:
```bash
# 检查是否在正确的目录
pwd  # 应该显示 .../enumerate_framework

# 检查Python版本
python --version  # 需要Python 3.7+

# 检查requests库是否安装
pip install requests
```

### 问题: 某个API测试失败

**可能原因**:
1. **网络问题**: 检查网络连接
2. **速率限制**: 等待几分钟后重试
3. **API变更**: API可能已更新，需要修改fetcher代码

**查看详细错误**:
```bash
python test_all_apis.py 2>&1 | tee test_output.log
```

### 问题: test_with_api_keys.py 显示"未配置"

**解决方案**:
```bash
# 1. 确保.env文件存在
ls -la .env

# 2. 检查.env文件内容
cat .env

# 3. 确保安装了python-dotenv
pip install python-dotenv

# 4. 确保环境变量格式正确（没有引号）
# 正确: YOUTUBE_API_KEY=AIzaSy...
# 错误: YOUTUBE_API_KEY="AIzaSy..."
```

## 📖 进阶使用

### 添加自定义测试

编辑 `test_all_apis.py` 或 `test_with_api_keys.py`，添加新的测试函数：

```python
def test_my_custom_api():
    from fetchers.npm import NPMFetcher
    fetcher = NPMFetcher()

    # 测试自定义的包
    results, api_info, question = fetcher.fetch(package='my-package')

    # 保存结果
    save_result("my_custom_test", {...})
```

### 生成完整测试集

```bash
# 生成所有API的测试用例（包括hash稀疏问题）
python main.py
```

这会生成 `output/test_cases.json`，包含：
- "列举全部"问题
- 对应的hash稀疏问题
- 完整的参考答案

## 📚 相关文档

- **[../API_CATALOG.md](../API_CATALOG.md)** - 完整的API目录（23个API详细说明）
- **[../NEW_APIS_SUMMARY.md](../NEW_APIS_SUMMARY.md)** - 新增API总结和理论意义
- **[../COMPLETION_REPORT.md](../COMPLETION_REPORT.md)** - 项目完成报告

## 💡 核心理念

**AI搜索的本质不在于模糊推理，而在于"列举全部"（Enumerate All）的能力。**

这个框架通过23个真实API验证：
- ✓ 模型是否能完整枚举所有结果
- ✓ 模型是否承认无法枚举
- ✓ 模型是否"假装枚举"（部分结果但声称完整）

## 🎯 下一步

1. **运行无需认证的测试**: `python test_all_apis.py`
2. **查看输出**: `ls output/api_tests/`
3. **（可选）配置API Key**: 编辑 `.env`
4. **（可选）测试需要Key的API**: `python test_with_api_keys.py`
5. **分析结果**: 使用JSON文件评估LLM的"列举全部"能力

---

**现在就开始**: `python test_all_apis.py` ✨
