# 元数据增强测试 - 深度枚举能力评估

## 🎯 核心理念

传统的"列举全部"测试太简单：
- **Level 1（基础）**: 列出所有X → 只需调用API
- **Level 2（增强）**: 列出所有X，**其中满足条件Y** → 需要获取每个项目的元数据并过滤

**难度提升的本质**：
```
简单：列出DBLP中YannLeCun的所有论文（422篇）
困难：列出DBLP中YannLeCun作为第2作者的所有论文（需要知道每篇论文的作者顺序！）
```

第二个问题真正测试AI是否能：
1. 完整枚举所有论文
2. 获取每篇论文的详细元数据（作者列表、作者位置）
3. 根据元数据精确过滤

---

## 📊 已实现的增强测试

### 1. DBLP - 计算机科学论文 ⭐⭐⭐

**元数据丰富度**: 极高（作者列表、位置、会议/期刊、年份、类型）

#### 基础问题
```
列出DBLP中作者Yann LeCun (PID: l/YannLeCun)的所有出版物
```

#### 增强问题（3个）

**问题1 - 作者位置过滤** (最难)
```
列出DBLP中作者Yann LeCun (PID: l/YannLeCun)作为第2作者的所有出版物

需要元数据：完整作者列表 + 作者顺序
难度：⭐⭐⭐ 需要解析每篇论文的作者列表并定位位置
```

**问题2 - 会议/期刊过滤**
```
列出DBLP中作者Yann LeCun (PID: l/YannLeCun)发表在CVPR会议的所有出版物

需要元数据：venue字段（会议/期刊名称）
难度：⭐⭐ 需要字符串匹配
```

**问题3 - 年份过滤**
```
列出DBLP中作者Yann LeCun (PID: l/YannLeCun)在2020年后发表的所有出版物

需要元数据：year字段
难度：⭐ 简单数值比较
```

#### 运行测试
```bash
python test_runners/academic_research/dblp.py
```

#### 预期输出
```
[基础问题] 列出所有出版物
  ✓ 找到 422 篇出版物

[增强问题 1/3] 列出作为第2作者的所有出版物
  ✓ 找到 38 篇（占比: 9.0%）

[增强问题 2/3] 列出发表在CVPR会议的所有出版物
  ✓ 找到 56 篇（占比: 13.3%）

[增强问题 3/3] 列出2020年后发表的所有出版物
  ✓ 找到 89 篇（占比: 21.1%）
```

---

### 2. GitHub - 代码仓库 ⭐⭐

**元数据丰富度**: 高（API已返回所有元数据）

#### 基础问题
```
列出GitHub上用户torvalds的所有仓库
```

#### 增强问题（3个）

**问题1 - Star数过滤**
```
列出GitHub上用户torvalds的所有仓库，其中star数超过1000的

需要元数据：stargazers_count字段
难度：⭐ 数值比较，API已返回
```

**问题2 - 编程语言过滤**
```
列出GitHub上用户torvalds的所有仓库，其中主语言是C的

需要元数据：language字段
难度：⭐ 字符串匹配，API已返回
```

**问题3 - 创建日期过滤**
```
列出GitHub上用户torvalds的所有仓库，其中在2010年后创建的

需要元数据：created_at字段
难度：⭐ 日期比较，API已返回
```

#### 运行测试
```bash
python test_runners/test_github_enhanced.py
```

---

## 🚀 运行所有增强测试

```bash
cd enumerate_framework
python test_enhanced_apis.py
```

输出目录：
```
output/api_tests/
├── academic_research/dblp.json     # DBLP综合测试结果
└── github_enhanced.json   # GitHub增强测试结果
```

---

## 📁 输出格式

每个增强测试的输出包含：

```json
{
  "api_name": "DBLP (Enhanced with Metadata Filtering)",
  "description": "测试AI的深度枚举能力",
  "difficulty_level": "Advanced (Level 2)",
  "tests": [
    {
      "author": "Yann LeCun",
      "pid": "l/YannLeCun",
      "base_test": {
        "question": "列出所有出版物",
        "total_count": 422,
        "publications": [...]
      },
      "enhanced_tests": [
        {
          "question": "列出作为第2作者的所有出版物",
          "filter_type": "author_position",
          "filter_value": 2,
          "total_count": 38,
          "percentage": "9.0%",
          "publications": [...]
        },
        ...
      ],
      "summary": {
        "total_publications": 422,
        "as_2nd_author": 38,
        "at_cvpr": 56,
        "since_2020": 89
      }
    }
  ]
}
```

---

## ⭐ 待实现的增强测试

### 3. Spotify - 音乐专辑 (需要API Key)

**增强问题设计：**
- 列出Taylor Swift的所有专辑，其中是studio albums的
- 列出Taylor Swift的所有专辑，其中在2020年后发行的
- 列出Taylor Swift的所有专辑，其中包含超过10首歌的

### 4. PubMed - 生物医学论文

**增强问题设计：**
- 列出某ORCID作者作为第一作者的所有论文
- 列出某ORCID作者发表在Nature/Science的所有论文
- 列出某ORCID作者在2020-2023年发表的所有论文

---

## 💡 增强测试的价值

### 1. **测试更深层的理解能力**
- 不仅要知道"有哪些论文"
- 还要理解"每篇论文的作者顺序、会议、年份等详细信息"

### 2. **更接近真实使用场景**
真实的研究场景往往需要过滤：
- "列出我作为第一作者的所有论文"
- "列出我在顶会发表的论文"
- "列出近5年的工作"

### 3. **验证完整性**
如果AI声称"列举了所有第2作者论文"，可以验证：
- 是否真的获取了所有论文？
- 是否正确解析了每篇论文的作者顺序？
- 是否有遗漏或错误？

### 4. **难度分级明确**
- Level 1: 简单API调用
- Level 2: API调用 + 元数据解析 + 过滤逻辑
- 可以清晰评估AI的能力层次

---

## 🔧 扩展到其他API

要为其他API添加增强测试，需要：

1. **在fetcher中添加元数据提取方法**
   ```python
   def fetch_with_metadata(self, ...):
       # 返回List[Dict]，每个Dict包含完整元数据
   ```

2. **添加过滤方法**
   ```python
   def filter_by_xxx(self, items_with_metadata, filter_value):
       # 根据元数据过滤
   ```

3. **创建增强测试模块**
   ```python
   # test_runners/test_xxx_enhanced.py
   # 包含1个基础 + 2-3个增强问题
   ```

4. **在test_enhanced_apis.py中注册**

---

## 📊 对比总结

| 测试类型 | 难度 | 需要的能力 | 示例 |
|---------|------|-----------|------|
| Level 1 (基础) | ⭐ | API调用 | 列出所有论文 |
| Level 2 (增强) | ⭐⭐⭐ | API调用 + 元数据解析 + 过滤 | 列出第2作者论文 |

**结论**: 增强测试真正测试了AI的"深度枚举"能力，而不仅仅是"表面枚举"！

---

**最后更新**: 2025-10-27
**版本**: v1.0 (初版)
**状态**: ✅ DBLP和GitHub已实现，Spotify和PubMed待实现
