# TODO: 标准化 `dblp.py` 的输出格式

此计划概述了将 `dblp.py` 的输出与新的标准化JSON格式对齐所需的修改。这些更改将主要影响 `dblp.py` 及其辅助模块 `dblp_utils.py`。

每个测试用例的目标格式为：
- **基础枚举:** `{ "question": "...", "answers": [...] }`
- **高级查询:** `{ "question": "...", "answers": [ { "answer": "...", "year": ..., "venue": ... } ] }`

## 1. 当前输出分析

- 测试运行器 `dblp.py` 生成一个JSON文件，其中包含一个结果列表，每个作者一个。
- 每个作者的结果包含一个 `base_test` 和一个 `enhanced_tests` 列表。
- **基础测试:**
  - 由 `utils.py` 中的 `create_test_result` 生成。
  - 当前输出是复杂的：`{"question": ..., "total_publications": ..., "all_publications": [...]}`。
  - **这与目标格式不符。**
- **增强测试:**
  - 由 `dblp_utils.py` 中的 `build_enhanced_result` 生成。
  - 当前输出也很复杂：`{"question": ..., "filter_type": ..., "total_count": ..., "publications": [...]}`。
  - **这与目标格式不符。**
- **答案条目格式:**
  - 所有测试都使用 `dblp_utils.py` 中的 `format_publication`。主要标识符是 `title`。
  - **这与目标格式不符，** 目标格式要求主要标识符在 `answer` 键下。

## 2. 修改计划

### A. 修改 `enumerate_framework/test_runners/academic_research/dblp_utils.py`

1.  **更新 `format_publication` 函数:**
    - 将 `title` 键重命名为 `answer`。
    - **当前输出项:** `{"rank": 1, "title": "A paper title", "year": 2024, ...}`
    - **目标输出项:** `{"rank": 1, "answer": "A paper title", "year": 2024, ...}`

2.  **更新 `build_enhanced_result` 函数:**
    - 必须重构此函数以返回简单的 `{ "question": "...", "answers": [...] }` 结构。
    - `publications` 键应重命名为 `answers`。
    - `formatted_pubs`（现在将包含带有 `answer` 键的对象）应成为 `answers` 键的值。
    - 从返回的字典中删除 `filter_type`、`filter_value`、`total_count` 和 `percentage` 等其他键，以简化测试用例。这些摘要信息已存在于作者的更高级别 `summary` 对象中。

### B. 修改 `enumerate_framework/test_runners/academic_research/dblp.py`

1.  **更新 `run` 函数的基础测试创建:**
    - 对 `create_test_result` 的调用必须调整，以使用将在 `utils.py` 中实现的新的、简化的函数（参见 `ai_ml/TODO-modify.md`）。
    - 调用应更改为将 `formatted_publications` 传递给 `answers` 参数。
    - **当前:** `create_test_result(identifier=pid, data=formatted_publications, data_key="publications", ...)`
    - **目标:** `create_test_result(question=question, answers=formatted_publications, ...)`

### C. 关于 `utils.py` 的说明

- 此计划依赖于 `enumerate_framework/test_runners/utils.py` 中 `create_test_result` 的修改，如 `ai_ml/TODO-modify.md` 计划中所述。这里将使用相同的重构后的实用工具函数。

通过实施这些更改，`dblp.json` 中每个测试用例的输出将符合新标准，同时保留按作者分组测试的整体结构。
