# AI/ML API 扩展实施计划 (TODO)

本文档概述了为增强项目的“枚举所有”测试能力，需要集成的三个新的 AI/ML API 源的实施计划。

---

## 1. Papers with Code API 集成

**目标**: 集成 Papers with Code API，以测试对学术论文、排行榜（Leaderboards）和 SOTA（State-of-the-Art）模型的枚举和高级查询能力。

### 1.1. Fetcher 实现

-   **文件**: `enumerate_framework/fetchers/ai_ml/paperswithcode.py`
-   **前置条件**: 研究其 API 是否需要认证或有速率限制。
-   **核心函数**:
    -   `get_leaderboard(task_id)`: 获取指定任务（如 "Image Classification on ImageNet"）的完整排行榜。
    -   `enumerate_papers_by_task(task_id)`: 枚举与特定任务相关的所有论文。
    -   `get_paper_details(paper_id)`: 获取单篇论文的详细信息，包括链接的代码库。
-   **需提取的元数据**:
    -   排行榜条目: `model_name`, `paper_title`, `metrics` (如: `top_1_accuracy`), `publication_year`, `framework` (如: PyTorch)。
    -   论文: `title`, `authors`, `published_date`, `code_repositories`。

### 1.2. Test Runner 实现

-   **文件**: `enumerate_framework/test_runners/ai_ml/test_paperswithcode.py`
-   **基础枚举测试**:
    -   "枚举'ImageNet'分类任务排行榜上的所有结果。"
-   **高级问题测试**:
    1.  **排名查询**: "列出 'ImageNet' 排行榜上 Top-1 准确率最高的 10 个模型。"
    2.  **条件过滤**: "查找所有在 2023 年后发布、有官方 PyTorch 实现的'目标检测'（Object Detection）论文。"
    3.  **SOTA 查询**: "在'SQuAD 2.0'问答任务上，当前排名第一的模型是什么，其 F1 分数是多少？"

---

## 2. Kaggle API 集成

**目标**: 集成 Kaggle API，重点测试围绕竞赛排行榜、数据集和代码（Notebooks）的枚举和复杂过滤能力。

### 2.1. Fetcher 实现

-   **文件**: `enumerate_framework/fetchers/ai_ml/kaggle.py`
-   **前置条件**:
    -   需要在环境中配置 `kaggle.json` API 密钥。应在文档中说明此步骤。
-   **核心函数**:
    -   `enumerate_competitions(category)`: 枚举特定类别的所有竞赛（如 "getting-started"）。
    -   `get_competition_leaderboard(competition_id)`: 获取指定竞赛的公开排行榜。
    -   `enumerate_datasets(query)`: 根据查询条件枚举数据集。
    -   `enumerate_notebooks(query)`: 根据查询条件枚举 Notebooks。
-   **需提取的元数据**:
    -   排行榜: `team_name`, `rank`, `score`。
    -   数据集: `title`, `author`, `votes`, `license`, `size`。
    -   Notebooks: `title`, `author`, `language`, `medal` (Gold, Silver, Bronze)。

### 2.2. Test Runner 实现

-   **文件**: `enumerate_framework/test_runners/ai_ml/test_kaggle.py`
-   **基础枚举测试**:
    -   "枚举所有‘Getting Started’类型的竞赛。"
-   **高级问题测试**:
    1.  **排行榜查询**: "列出 'Titanic: Machine Learning from Disaster' 竞赛排行榜上排名前 20 的团队及其分数。"
    2.  **资源过滤**: "查找所有获得了金牌（Gold Medal）荣誉的公开 Python Notebooks。"
    3.  **数据集元数据查询**: "枚举所有使用 'CC0: Public Domain' 许可证并且投票数超过 1000 次的数据集。"

---

## 3. Hugging Face Leaderboards 功能增强

**目标**: 扩展现有的 Hugging Face fetcher，专门增加对公开排行榜（如 Open LLM Leaderboard）的查询和测试能力。

### 3.1. Fetcher 修改

-   **文件**: `enumerate_framework/fetchers/ai_ml/huggingface.py` (修改现有文件)
-   **新增核心函数**:
    -   `get_leaderboard(leaderboard_id="open-llm-leaderboard")`: 从 Hugging Face Hub 拉取并解析指定的排行榜数据。
-   **需提取的元数据**:
    -   `model`, `author`, `likes`, `params`, `license`, `average_score`, 以及各分项基准测试分数 (如 `ARC`, `MMLU` 等)。

### 3.2. Test Runner 实现

-   **文件**: `enumerate_framework/test_runners/ai_ml/test_huggingface_leaderboard.py` (建议创建新文件以保持清晰)
-   **基础枚举测试**:
    -   "枚举 Open LLM Leaderboard 上的所有模型及其平均分。"
-   **高级问题测试**:
    1.  **排序与过滤**: "列出 Open LLM Leaderboard 上平均分排名前 10，且参数量少于 100 亿（10B）的模型。"
    2.  **特定指标查询**: "在排行榜上，查找在 'MMLU' 基准测试中得分最高的模型。"
    3.  **多条件查询**: "筛选出排行榜上所有由 'meta-llama' 组织发布并且使用 'Llama 2' 许可证的模型。"
