# TODO: 标准化代码生态系统的输出格式

此计划概述了将 `code_ecosystem` 目录中所有测试运行器的输出与新的标准化JSON格式对齐所需的修改。

每个测试用例的目标格式为：
- **基础枚举:** `{ "question": "...", "answers": [...] }`
- **高级查询:** `{ "question": "...", "answers": [ { "answer": "...", "metadata_key": "value", ... } ] }`

## 1. 当前输出分析

此目录包含多种类型的测试运行器，其输出结构各不相同。

- **基于包的运行器** (`test_npm.py`, `test_pypi.py`, `test_crates.py` 等):
  - **结构:** 这些运行器使用 `code_utils.py` 中的辅助函数 (`build_base_result`, `build_enhanced_result`) 来创建测试用例。最终输出是每个包的自定义对象，包含 `base_test` 和 `enhanced_tests`。
  - **问题:** 这些测试用例的格式不标准（例如，使用 `versions` 和 `total_count` 键）。答案对象中的主要标识符是 `version`。这与目标格式不符。

- **`test_github.py`**:
  - **结构:** 此运行器为其结果手动构建了完全自定义的字典结构，使用 `repositories` 和 `total_count` 等键。
  - **问题:** 格式完全不标准。答案对象中的主要标识符是 `name`。

- **`test_homebrew.py`**:
  - **结构:** 此运行器使用主要的 `utils.py:create_test_result`。
  - **问题:** 其输出格式与旧的 `utils.py` 函数绑定，与新标准不符。

## 2. 修改计划

### A. 修改 `enumerate_framework/test_runners/code_ecosystem/code_utils.py` (高影响)

这是大多数包运行器的核心更改。

1.  **更新格式化辅助函数:** 必须修改任何格式化结果项的函数（例如 `format_version_basic`），将主要标识符键从 `version` 重命名为 `answer`。
2.  **重构 `build_base_result`:** 更改函数以返回简单的 `{ "question": ..., "answers": [...] }` 结构。`versions` 键应变为 `answers`，并移除 `total_count`。
3.  **重构 `build_enhanced_result`:** 类似地，更改此函数以返回简单的 `{ "question": ..., "answers": [...] }` 结构。`versions` 键应变为 `answers`，并从测试用例本身中移除 `filter_type`、`total_count` 等额外的键。

### B. 修改基于包的运行器 (例如 `test_npm.py`, `test_pypi.py`)

1.  **更新调用:** 修改 `code_utils.py` 后，每个测试运行器中对 `build_base_result` 和 `build_enhanced_result` 的调用需要更新以传递正确的参数。
2.  **保留结构:** 可以保留为每个包创建结果对象（例如 `package_result`）的总体结构，该对象包含一个标准化的测试用例列表。

### C. 修改 `test_github.py`

1.  **采用标准实用工具:** 必须重构此文件，停止构建自定义字典，而是为每个测试使用 `utils.py` 中新的、标准化的 `create_test_result`。
2.  **标准化答案格式:** 必须修改创建仓库答案字典的逻辑，将 `name` 键重命名为 `answer`。
3.  **简化输出:** 最终输出应为一个简单的测试用例列表，自定义的 `summary` 对象应被移除或单独处理。

### D. 修改 `test_homebrew.py`

1.  **更新函数调用:** 更新对 `create_test_result` 的调用，以匹配 `ai_ml/TODO-modify.md` 计划中定义的新的、简化的签名。
2.  **示例:**
    - **当前:** `create_test_result(identifier=formula, data=versions, data_key="versions", ...)`
    - **目标:** `create_test_result(question=question, answers=versions, ...)`

### E. 关于 `utils.py` 的说明

- 所有修改都依赖于 `enumerate_framework/test_runners/utils.py` 中 `create_test_result` 的核心更改，如之前的计划中所述。
