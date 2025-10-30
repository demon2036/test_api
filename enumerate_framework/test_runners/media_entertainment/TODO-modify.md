# TODO: 标准化 Media & Entertainment 的输出格式

此计划概述了将 `test_spotify.py`、`test_tmdb.py` 和 `test_youtube.py` 的输出与新的标准化JSON格式对齐所需的修改。

每个测试用例的目标格式为：
- **基础枚举:** `{ "question": "...", "answers": [...] }`
- **高级查询:** `{ "question": "...", "answers": [ { "answer": "...", "metadata_key": "value", ... } ] }`

## 1. 当前输出分析

此目录中的测试运行器不使用通用的 `utils.create_test_result`，并且每个都有独特的、非标准的输出格式。

- **`test_spotify.py`**:
  - **结构:** 为每个艺术家创建一个测试列表，但每个测试用例都是一个字典 `{"question": ..., "total": ..., "all_items": [...]}`。
  - **问题:** `total` 和 `all_items` 键不正确。它们应被替换为单个 `answers` 键。

- **`test_tmdb.py`**:
  - **结构:** 为每个人创建一个单一、庞大且非结构化的字典，不同查询的结果嵌套在 `sample_credits`、`actor_and_producer`、`science_fiction_works` 等各种键下。
  - **问题:** 这是最不标准的格式。需要进行重大重构，以创建一个包含清晰测试用例的列表，每个测试用例都有 `question` 和 `answers` 键。答案对象中的主要标识符（例如 `title`）需要重命名为 `answer`。

- **`test_youtube.py`**:
  - **结构:** 为每个频道创建一个带有嵌套结果的字典。高级测试结果位于名为 `answer`（单数）的键下，并包含一个额外的 `total` 键。“观看次数最多”的测试返回单个对象而不是列表。
  - **问题:** 结构不是一个简单的测试用例列表。键不正确（`answer` 而不是 `answers`），并且格式不一致（对象与列表）。主要标识符 `title` 需要重命名为 `answer`。

## 2. 修改计划

### A. 通用更改：采用 `utils.create_test_result`

所有三个测试运行器都应重构，以使用 `enumerate_framework/test_runners/utils.py` 中新的、标准化的 `create_test_result` 函数（如 `ai_ml/TODO-modify.md` 计划中所定义）。这将确保整个项目的一致性。

### B. 修改 `test_spotify.py`

1.  **重构测试用例创建:** 将手动创建的字典 `{"question": ..., "total": ..., "all_items": [...]}` 替换为对 `utils.create_test_result` 的调用。
2.  **更新数据键:** 将 `all_items` 中的数据传递给新函数的 `answers` 参数。

### C. 修改 `test_tmdb.py`

1.  **完全重构:** 重新设计整个结果生成逻辑。脚本应生成一个标准的测试用例字典列表，而不是为每个人生成一个大的字典。
2.  **创建清晰的测试用例:**
    - 为“列出所有作品”创建一个“基础”测试用例。
    - 为每个高级过滤器（例如“演员兼制片人”、“科幻作品”）创建独立的、清晰的测试用例对象。
3.  **标准化答案格式:**
    - 对于 `answers` 列表中的每个答案对象，主要标识符（例如 `title` 或 `name`）必须重命名为 `answer`。这可能需要修改测试运行器中的格式化逻辑。
4.  **为所有生成的测试用例使用 `utils.create_test_result`**。

### D. 修改 `test_youtube.py`

1.  **重构结果结构:** 重新设计逻辑，为每个频道生成一个扁平的测试用例列表，而不是嵌套的字典。
2.  **创建清晰的测试用例:**
    - 为“列出所有视频”创建一个“基础”测试用例。
    - 为高级查询（长视频、热门视频、观看次数最多的视频）创建独立的测试用例对象。
3.  **标准化答案格式:**
    - 结果列表的键必须是 `answers`。
    - 对于“观看次数最多的视频”测试，单个结果对象必须包装在一个列表中：`answers: [most_viewed_object]`。
    - 在每个答案对象中，`title` 键必须重命名为 `answer`。
4.  **为所有生成的测试用例使用 `utils.create_test_result`**。
