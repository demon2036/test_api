# TODO: 标准化 `test_huggingface.py` 的输出格式

此计划概述了将 `test_huggingface.py` 的输出与新的标准化JSON格式对齐所需的修改。

目标格式为：
- **基础枚举:** `{ "question": "...", "answers": [...] }`
- **高级查询:** `{ "question": "...", "answers": [ { "answer": "...", "downloads": ..., "likes": ... } ] }`

## 1. 当前输出分析

- **基础测试 (`_run_basic_resource_test`):**
  - 当前使用 `utils.py` 中的 `create_test_result`，它会生成一个复杂的对象，包含 `total_models`、`sample_models` 和 `all_models` 等键。
  - **这与目标格式不符。**

- **增强测试 (`_run_enhanced_test`):**
  - 使用本地的 `_extract_metadata` 函数和 `create_test_result`。
  - 输出在 `all_models` 这样的键下包含一个字典列表。
  - 列表中的每个字典都使用 `id` 键作为主要标识符 (例如, `"id": "model-name"`)。
  - **这与目标格式不符。** 主键应为 `answers`，并且每个对象内部的标识符键应为 `answer`。

## 2. 修改计划

### A. 修改 `enumerate_framework/test_runners/ai_ml/test_huggingface.py`

1.  **更新 `_extract_metadata` 函数:**
    - 此函数处理增强测试的结果。
    - 必须修改它，将其生成的字典中的 `id` 键重命名为 `answer`。
    - **当前输出项:** `{'id': 'model-name', 'downloads': 123, ...}`
    - **目标输出项:** `{'answer': 'model-name', 'downloads': 123, ...}`

2.  **更新对 `create_test_result` 的调用:**
    - 传递给 `create_test_result` 的参数需要更新，以匹配我们将在 `utils.py` 中定义的新函数签名。
    - `data` 参数将变为 `answers`，`data_key` 将被移除。

### B. 修改 `enumerate_framework/test_runners/utils.py` (跨领域更改)

1.  **重构 `create_test_result` 函数:**
    - 当前函数会生成多个键 (`total_*`, `sample_*`, `all_*`)。
    - 需要将其替换为一个更简单的版本，以生成目标格式。
    - **新的建议签名:** `create_test_result(question, answers, api_info=None, **extra_fields)`
    - **新的实现:**
      ```python
      from datetime import datetime

      def create_test_result(question, answers, api_info=None, **extra_fields):
          result = {
              "question": question,
              "answers": answers,
              "timestamp": datetime.now().isoformat()
          }
          if api_info:
              result["api_info"] = api_info
          result.update(extra_fields)
          return result
      ```
    - 此更改将影响所有导入并使用此函数的测试运行器，这正是标准化的目的。

### C. 更新 `test_huggingface.py` 中的 `_run_basic_resource_test` 和 `_run_enhanced_test`

1.  **`_run_basic_resource_test`:**
    - 对 `create_test_result` 的调用必须从：
      ```python
      create_test_result(
          identifier=...,
          question=question,
          api_info=api_info,
          data=items,
          data_key=resource_type,
          ...
      )
      ```
    - 更改为：
      ```python
      create_test_result(
          question=question,
          answers=items, # `items` 是模型/数据集名称的列表
          api_info=api_info,
          ...
      )
      ```

2.  **`_run_enhanced_test`:**
    - 对 `create_test_result` 的调用必须从：
      ```python
      create_test_result(
          identifier=...,
          question=test_spec["question"],
          api_info=api_info,
          data=answer_with_metadata,
          data_key=resource_type,
          ...
      )
      ```
    - 更改为：
      ```python
      create_test_result(
          question=test_spec["question"],
          answers=answer_with_metadata, # 这现在包含了带有 'answer' 键的对象
          api_info=api_info,
          ...
      )
      ```
