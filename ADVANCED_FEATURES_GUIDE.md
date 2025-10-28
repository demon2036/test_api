# Docker Hub & Homebrew 高级功能使用指南

本指南介绍 Docker Hub 和 Homebrew fetchers 的高级过滤功能，这些功能实现了 GEMINI.md 中提到的"Advanced Questions"。

---

## 🐳 Docker Hub 高级功能

Docker Hub fetcher 现在支持获取完整的标签元数据，并提供多种过滤和排序方法。

### 新增方法

#### 1. `fetch_with_metadata(image, limit=1000)`

获取镜像的所有标签，包含完整元数据。

**返回的元数据包括：**
- `name`: 标签名称
- `last_pushed`: 最后推送时间
- `last_pulled`: 最后拉取时间
- `size`: 镜像大小（字节）
- `architectures`: 支持的架构列表（如 `['amd64', 'arm64']`）
- `os_list`: 支持的操作系统列表（如 `['linux', 'windows']`）
- `images`: 完整的镜像清单数组

**使用示例：**
```python
from fetchers.docker import DockerFetcher

fetcher = DockerFetcher()

# 获取 Python 镜像的所有标签（含元数据）
tags, api_info, question = fetcher.fetch_with_metadata(image='python', limit=100)

# 查看第一个标签的元数据
print(tags[0])
# 输出: {
#   'name': 'latest',
#   'last_pushed': '2025-10-24T21:10:26.545511Z',
#   'size': 394800000,
#   'architectures': ['amd64', 'arm64', '386', ...],
#   'os_list': ['linux', 'windows'],
#   'images': [...]
# }
```

#### 2. `filter_by_name_pattern(tags_with_metadata, pattern)`

根据名称模式过滤标签（不区分大小写）。

**使用示例：**
```python
# 查找所有基于 alpine 的标签
alpine_tags = fetcher.filter_by_name_pattern(tags, "alpine")
print(f"找到 {len(alpine_tags)} 个 alpine 标签")
print([t['name'] for t in alpine_tags[:5]])

# 查找所有 slim 标签
slim_tags = fetcher.filter_by_name_pattern(tags, "slim")
```

**对应的 GEMINI.md 高级问题：**
> "List all tags for the 'python' image that are based on 'alpine'."

#### 3. `filter_by_architecture(tags_with_metadata, arch)`

根据架构过滤标签。

**使用示例：**
```python
# 查找所有支持 arm64 架构的标签
arm_tags = fetcher.filter_by_architecture(tags, "arm64")

# 查找所有支持 amd64 架构的标签
amd_tags = fetcher.filter_by_architecture(tags, "amd64")

# 支持的架构: amd64, arm64, arm, 386, ppc64le, riscv64, s390x
```

**对应的 GEMINI.md 高级问题：**
> "List all tags for the 'nginx' image that are for a specific architecture (e.g., 'arm64')."

#### 4. `sort_by_push_time(tags_with_metadata, reverse=True)`

按推送时间排序标签。

**使用示例：**
```python
# 获取最近推送的标签（降序，最新的在前）
recent_tags = fetcher.sort_by_push_time(tags, reverse=True)
print("最新的5个标签:")
for tag in recent_tags[:5]:
    print(f"  {tag['name']} - {tag['last_pushed'][:19]}")

# 获取最早推送的标签（升序，最旧的在前）
oldest_tags = fetcher.sort_by_push_time(tags, reverse=False)
```

**对应的 GEMINI.md 高级问题：**
> "Find the most recently pushed tag for the 'ubuntu' image."

### 完整示例：组合过滤

```python
from fetchers.docker import DockerFetcher

fetcher = DockerFetcher()

# 1. 获取所有标签（含元数据）
tags, _, _ = fetcher.fetch_with_metadata(image='python', limit=200)

# 2. 查找基于 alpine 的标签
alpine_tags = fetcher.filter_by_name_pattern(tags, "alpine")

# 3. 进一步过滤支持 arm64 架构的 alpine 标签
alpine_arm64 = fetcher.filter_by_architecture(alpine_tags, "arm64")

# 4. 按推送时间排序，找出最新的
latest_alpine_arm64 = fetcher.sort_by_push_time(alpine_arm64, reverse=True)

print(f"最新的 alpine + arm64 标签: {latest_alpine_arm64[0]['name']}")
```

---

## 🍺 Homebrew 高级功能

Homebrew fetcher 现在支持获取完整的 formula 元数据，并提供多种过滤和信息提取方法。

### 新增方法

#### 1. `fetch_with_metadata(formula)`

获取单个 formula 的完整详细信息。

**返回的元数据包括：**
- `name`: Formula 名称
- `desc`: 描述
- `versions`: 版本信息（stable, head, bottle）
- `service`: Service 配置（如有）
- `keg_only`: 是否 keg-only
- `keg_only_reason`: Keg-only 原因
- `aliases`: 别名列表
- `dependencies`: 依赖列表
- `deprecated`: 是否已弃用
- 以及其他详细信息

**使用示例：**
```python
from fetchers.homebrew import HomebrewFetcher

fetcher = HomebrewFetcher()

# 获取 redis 的完整信息
redis_data, api_info, question = fetcher.fetch_with_metadata(formula='redis')

print(f"名称: {redis_data['name']}")
print(f"描述: {redis_data['desc']}")
print(f"版本: {redis_data['versions']['stable']}")
print(f"别名: {redis_data['aliases']}")
print(f"有 service: {redis_data['service'] is not None}")
```

#### 2. `fetch_all_formulae_with_metadata(max_formulae=10000)`

获取所有 formulae 的完整元数据（替代原来只返回名称的方法）。

**使用示例：**
```python
# 获取所有 formulae（含元数据）
formulae, api_info, question = fetcher.fetch_all_formulae_with_metadata(max_formulae=500)

print(f"获取了 {len(formulae)} 个 formulae")
```

#### 3. `filter_with_service(formulae_with_metadata)`

过滤有 service 定义的 formulae。

**使用示例：**
```python
# 获取所有 formulae
formulae, _, _ = fetcher.fetch_all_formulae_with_metadata()

# 过滤有 service 的 formulae
service_formulae = fetcher.filter_with_service(formulae)

print(f"有 service 的 formulae: {[f['name'] for f in service_formulae]}")
```

**对应的 GEMINI.md 高级问题：**
> "List all available services for the 'postgresql' formula."

#### 4. `filter_keg_only(formulae_with_metadata)`

过滤 keg-only 的 formulae。

**使用示例：**
```python
# 过滤 keg-only 的 formulae
keg_only_formulae = fetcher.filter_keg_only(formulae)

print(f"Keg-only formulae: {[f['name'] for f in keg_only_formulae[:10]]}")
```

**对应的 GEMINI.md 高级问题：**
> "Check if the 'python' formula is keg-only and why."

#### 5. `filter_with_aliases(formulae_with_metadata)`

过滤有别名的 formulae。

**使用示例：**
```python
# 过滤有别名的 formulae
aliased_formulae = fetcher.filter_with_aliases(formulae)

for f in aliased_formulae[:5]:
    print(f"{f['name']}: {f['aliases']}")
```

**对应的 GEMINI.md 高级问题：**
> "List all aliases for the 'openssl@3' formula."

#### 6. `filter_deprecated(formulae_with_metadata)`

过滤已弃用的 formulae。

**使用示例：**
```python
# 过滤已弃用的 formulae
deprecated = fetcher.filter_deprecated(formulae)
```

### 辅助方法

#### 7. `get_service_info(formula_data)`

提取 formula 的 service 详细信息。

**使用示例：**
```python
# 获取 redis 的 service 信息
redis_data, _, _ = fetcher.fetch_with_metadata('redis')
service_info = fetcher.get_service_info(redis_data)

if service_info:
    print(f"运行命令: {service_info['run_command']}")
    print(f"运行类型: {service_info['run_type']}")
    print(f"日志路径: {service_info['log_path']}")
```

**返回的 service 信息包括：**
- `name`: Formula 名称
- `run_command`: 运行命令
- `run_type`: 运行类型（immediate, interval 等）
- `keep_alive`: Keep-alive 配置
- `working_dir`: 工作目录
- `log_path`: 日志路径
- `error_log_path`: 错误日志路径

#### 8. `get_keg_only_reason(formula_data)`

获取 formula 的 keg-only 原因。

**使用示例：**
```python
# 检查 python 是否 keg-only 以及原因
python_data, _, _ = fetcher.fetch_with_metadata('python')
reason = fetcher.get_keg_only_reason(python_data)

if reason:
    print(f"{reason['name']} is keg-only")
    print(f"原因: {reason['reason']}")
    print(f"说明: {reason['explanation']}")
else:
    print("Python 不是 keg-only")
```

#### 9. `get_aliases(formula_data)`

获取 formula 的别名列表。

**使用示例：**
```python
# 获取 openssl@3 的别名
openssl_data, _, _ = fetcher.fetch_with_metadata('openssl@3')
alias_info = fetcher.get_aliases(openssl_data)

print(f"{alias_info['name']} 的别名: {alias_info['aliases']}")
```

### 完整示例：组合过滤

```python
from fetchers.homebrew import HomebrewFetcher

fetcher = HomebrewFetcher()

# 1. 获取所有 formulae（含元数据）
formulae, _, _ = fetcher.fetch_all_formulae_with_metadata()

# 2. 找出有 service 的 formulae
service_formulae = fetcher.filter_with_service(formulae)
print(f"有 service 的 formulae: {len(service_formulae)} 个")

# 3. 进一步过滤：有 service 但不是 keg-only 的
service_not_keg = [f for f in service_formulae if not f.get('keg_only', False)]
print(f"有 service 且不是 keg-only: {len(service_not_keg)} 个")

# 4. 获取这些 formulae 的 service 信息
for formula in service_not_keg[:3]:
    service_info = fetcher.get_service_info(formula)
    print(f"\n{service_info['name']}:")
    print(f"  运行命令: {service_info['run_command']}")
    print(f"  日志路径: {service_info['log_path']}")

# 5. 查找有别名的 formulae
aliased = fetcher.filter_with_aliases(formulae)
print(f"\n有别名的 formulae: {len(aliased)} 个")

# 6. 查找已弃用的 formulae
deprecated = fetcher.filter_deprecated(formulae)
print(f"已弃用的 formulae: {len(deprecated)} 个")
```

---

## 🧪 测试脚本

我们提供了两个完整的测试脚本来验证所有功能：

### Docker Hub 测试

```bash
python test_docker_advanced.py
```

该脚本测试：
- 获取元数据
- 按名称模式过滤（alpine, slim）
- 按架构过滤（arm64, amd64）
- 按推送时间排序
- 组合过滤

### Homebrew 测试

```bash
python test_homebrew_advanced.py
```

该脚本测试：
- 获取单个 formula 的元数据
- 获取所有 formulae 的元数据
- 过滤有 service 的 formulae
- 过滤 keg-only 的 formulae
- 过滤有别名的 formulae
- 过滤已弃用的 formulae
- 提取 service 信息
- 获取 keg-only 原因
- 获取别名列表
- 组合过滤

---

## ✅ 实现的高级问题对照表

### Docker Hub

| GEMINI.md 中的问题 | 实现方法 | 状态 |
|-------------------|---------|------|
| List all tags for the 'python' image that are based on 'alpine' | `filter_by_name_pattern(tags, "alpine")` | ✅ |
| Find the most recently pushed tag for the 'ubuntu' image | `sort_by_push_time(tags, reverse=True)[0]` | ✅ |
| List all tags for the 'nginx' image that are for a specific architecture (e.g., 'arm64') | `filter_by_architecture(tags, "arm64")` | ✅ |

### Homebrew

| GEMINI.md 中的问题 | 实现方法 | 状态 |
|-------------------|---------|------|
| List all available services for the 'postgresql' formula | `get_service_info(formula_data)` | ✅ |
| Check if the 'python' formula is keg-only and why | `get_keg_only_reason(formula_data)` | ✅ |
| List all aliases for the 'openssl@3' formula | `get_aliases(formula_data)` | ✅ |

---

## 🎯 设计原则

这些高级功能遵循 DBLP fetcher 的设计模式，采用**两阶段架构**：

1. **阶段一：Fetch with Rich Metadata**
   获取完整的 API 数据，保留所有元数据字段，不丢弃任何信息。

2. **阶段二：Client-side Filtering**
   提供多个可组合的过滤函数，支持复杂的查询组合。

这种设计完全符合 "Enumerate All" 的核心理念：
- **Completeness（完整性）**: 先获取所有数据
- **Determinism（确定性）**: 过滤在客户端进行，可重现
- **Composability（可组合性）**: 过滤函数可以链式组合使用

---

## 📝 向后兼容性

所有原有的方法保持不变，确保向后兼容：

- `DockerFetcher.fetch()` - 仍然只返回标签名称列表
- `HomebrewFetcher.fetch()` - 仍然返回版本和变体
- `HomebrewFetcher.fetch_all_formulae()` - 仍然只返回名称列表

新的 `*_with_metadata()` 方法作为增强版本存在，用户可以选择使用。
