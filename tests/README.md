# 测试框架文档

完整的单元测试、回归测试和代码审查框架，用于验证 PPTX 转 HTML 的内容完整性。

## 📋 概览

| 测试类型 | 文件 | 用途 | 命令 |
|---------|------|------|------|
| **单元测试** | `test_normalise_pptx.py` | 验证 `_normalise_pptx()` 函数的各种场景 | `pytest test_normalise_pptx.py -v` |
| **回归测试** | `regression_test_pptx.py` | 对真实 PPTX 文件进行完整性检查 | `python regression_test_pptx.py file.pptx` |
| **代码审查** | `code_review_checklist.py` | 检查代码中的危险模式和截断操作 | `python code_review_checklist.py --check file.py` |
| **测试运行器** | `run_tests.py` | 统一运行所有测试 | `python run_tests.py` |

---

## 🧪 单元测试

### 文件位置
`tests/test_normalise_pptx.py`

### 测试覆盖

#### 1. 数据完整性测试 (`TestNormalisePptxDataIntegrity`)

| 测试方法 | 描述 | 验证点 |
|---------|------|-------|
| `test_no_content_loss_in_bullets` | **109 个列表项不丢失** | - 输入 109 项 → 输出 109 项<br>- 首项和末项都存在<br>- 没有项被跳过 |
| `test_no_truncation_in_table_caption` | **表格 caption 不截断** | - 250 字文本完整保留<br>- 没有 [:200] 截断<br>- 长文本不被切割 |
| `test_smartart_not_lost` | **SmartArt 内容完整** | - 所有 SmartArt 项在 caption<br>- body_text 也在 caption<br>- 两者都被包含 |
| `test_table_structure_preserved` | **表格结构保留** | - headers 完整<br>- rows 完整<br>- 列名和行数都对 |
| `test_caption_uses_newline_not_space` | **使用换行符分隔** | - caption 包含 `\n`<br>- 所有内容项都在<br>- 分隔正确 |
| `test_no_slide_skipping` | **所有 slide 都处理** | - 输入 3 个 → 输出 3 个<br>- 没有遗漏或合并<br>- 核心不变量 |
| `test_empty_text_handling` | **空文本被过滤** | - 空字符串不添加<br>- 空白不添加<br>- 只有有效项 |
| `test_type_promotion_to_stats` | **数字内容升级** | - content-list 升级为 stats<br>- 数字被识别<br>- 类型正确 |
| `test_image_always_included` | **图像保留** | - 图像在 entry 中<br>- URL 正确<br>- 各类型都有 |

#### 2. 回归测试 (`TestNormalisePptxRegressions`)

| 测试方法 | 关键 Bug | 验证修复 |
|---------|---------|---------|
| `test_regression_bug_200char_truncation` | **200 字截断 bug** | 300+ 字 caption 完整保留 |
| `test_regression_109_items_loss` | **109 项只显示 1 项** | 所有 109 项都输出 |

#### 3. 边界情况测试 (`TestNormalisePptxEdgeCases`)

| 测试方法 | 场景 | 验证 |
|---------|------|------|
| `test_multiple_tables_uses_first` | 多个表格 | 使用第一个 + 其他转 caption |
| `test_table_without_headers` | 无表头表格 | 处理正确 |
| `test_mixed_content_types` | 混合内容 | 所有类型都保留 |

### 运行单元测试

```bash
# 安装依赖
pip install pytest

# 运行所有单元测试
pytest tests/test_normalise_pptx.py -v

# 运行特定测试
pytest tests/test_normalise_pptx.py::TestNormalisePptxDataIntegrity::test_no_content_loss_in_bullets -v

# 生成覆盖率报告
pytest tests/test_normalise_pptx.py --cov=scripts.generate_slides
```

### 预期结果

```
✅ 所有 15 个单元测试通过
- 0 个失败
- 0 个跳过
- 耗时 < 1s
```

---

## 🔄 回归测试

### 文件位置
`tests/regression_test_pptx.py`

### 功能

对**真实 PPTX 文件**进行完整性检查，验证：

1. **Slide 数量**: 输入 N 个 → 输出 N 个（无遗漏）
2. **文本内容**: 所有 body_paragraphs 都被保留
3. **表格结构**: 表头 + 行数完整
4. **表格 Caption**: 完整保留，无截断
5. **SmartArt**: 所有项都被保留
6. **图像**: 首选图像被保留

### 运行回归测试

```bash
# 基本检查
python tests/regression_test_pptx.py /path/to/file.pptx

# 生成 JSON 报告
python tests/regression_test_pptx.py /path/to/file.pptx --json report.json

# 生成 HTML 报告
python tests/regression_test_pptx.py /path/to/file.pptx --html --html-path report.html

# 详细输出
python tests/regression_test_pptx.py /path/to/file.pptx --verbose
```

### 输出示例

```
🔍 检查 PPTX 文件: /path/to/001.pptx
============================================================

📥 Step 1: 提取 PPTX 内容...
  ✓ 成功提取 10 个 slide

🔄 Step 2: 规范化 → outline 格式...
  ✓ 转换 10 个 outline entry

✓ Step 3: 检查完整性...
  ✓ Slide 数量匹配: 10 = 10

📊 完整性检查报告
============================================================
文件: 001.pptx
检查时间: 2025-03-19T14:30:45.123456
结果: ✅ PASS

📊 指标:
  - 输入 slides: 10
  - 输出 slides: 10
  - 检测到的问题: 0

============================================================

📄 JSON 报告已保存: /path/to/001.integrity.json
🌐 HTML 报告已保存: /path/to/001.integrity.html
```

### JSON 报告示例

```json
{
  "file": "/path/to/001.pptx",
  "timestamp": "2025-03-19T14:30:45.123456",
  "passed": true,
  "issues": [],
  "metrics": {
    "input_slides": 10,
    "output_slides": 10
  },
  "slides": [
    {
      "index": 1,
      "issues": []
    },
    ...
  ]
}
```

---

## 👀 代码审查

### 文件位置
`tests/code_review_checklist.py`

### 检查的危险模式

#### 🔴 关键 (Critical) — 必须避免

| 模式 | 描述 | 风险 | 例子 |
|------|------|------|------|
| `[:N]` | 字符串截断 | 内容丢失 | `caption[:200]` |
| `all_items[0]` | 只取首项 | 其他全丢失 | `all_items[0]` |
| `' '.join()[:N]` | join 后截断 | 极易丢失 | `' '.join(items)[:200]` |
| `entry['items'] = []` | 清空列表 | 所有项丢失 | `entry['items'] = []` |
| `return []` | 返回空列表 | 所有数据丢失 | `return []` |
| `break` | 提前退出 | 后续 slides 丢失 | `if condition: break` |

#### 🟡 高风险 (High)

| 模式 | 描述 | 风险 |
|------|------|------|
| `all_items[:N]` | 列表切片限制 | 后面项丢失 |
| `body_texts[0]` | 只取首个 body_text | 其他丢失 |
| `continue` | 跳过处理 | slide 被遗漏 |
| `.get()[:N]` | 获取后切片 | 截断内容 |

#### ✅ 必需模式

| 模式 | 原因 |
|------|------|
| `all_items = body_texts + table_lines + smartart_texts` | 合并所有内容来源 |
| `entry['items'] = all_items` | 完整保留所有内容 |
| `caption_parts.extend(body_texts)` | 包含 body 文本 |
| `caption_parts.extend(smartart_texts)` | 包含 SmartArt |
| `'\n'.join()` | 使用换行符分隔 |

### 运行代码审查

```bash
# 显示检查清单
python tests/code_review_checklist.py

# 检查特定文件
python tests/code_review_checklist.py --check scripts/generate_slides.py

# 生成 HTML 报告
python tests/code_review_checklist.py --check scripts/generate_slides.py --html report.html

# 详细输出
python tests/code_review_checklist.py --check scripts/generate_slides.py --verbose
```

### 输出示例

```
🔍 检查文件: scripts/generate_slides.py
======================================================================

🚨 检查危险模式...
  ✓ 未检测到任何危险模式

✅ 检查必需模式...
  ✓ 所有必需模式都存在

======================================================================
```

---

## 🚀 统一测试运行器

### 使用 `run_tests.py`

```bash
# 运行所有测试
python tests/run_tests.py

# 仅运行单元测试
python tests/run_tests.py --unit

# 仅运行回归测试
python tests/run_tests.py --regression /path/to/file.pptx

# 仅运行代码审查
python tests/run_tests.py --review

# 审查特定文件
python tests/run_tests.py --review scripts/generate_slides.py
```

### 输出示例

```
🚀 运行完整测试套件...

======================================================================
🧪 运行单元测试
======================================================================
tests/test_normalise_pptx.py::TestNormalisePptxDataIntegrity::test_no_content_loss_in_bullets PASSED
...
15 passed in 0.45s

======================================================================
👀 运行代码审查
======================================================================
🔍 检查文件: scripts/generate_slides.py
✓ 所有检查通过

======================================================================
📊 测试总结
======================================================================
单元测试: ✅ PASS
代码审查: ✅ PASS

总体: 2/2 通过

✅ 所有测试通过！
```

---

## 📊 CI/CD 集成

### GitHub Actions 示例

```yaml
name: PPTX Integrity Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run unit tests
        run: pytest tests/test_normalise_pptx.py -v
      
      - name: Run code review
        run: python tests/code_review_checklist.py --check scripts/generate_slides.py
      
      - name: Run regression tests (on real PPTXs)
        run: |
          for pptx in tests/fixtures/*.pptx; do
            python tests/regression_test_pptx.py "$pptx" --json "${pptx%.pptx}.json"
          done
```

---

## 🔧 添加新的测试

### 添加单元测试

在 `test_normalise_pptx.py` 中添加新测试方法：

```python
def test_your_scenario(self):
    """描述你的测试场景"""
    raw_slides = [
        {
            'number': 1,
            'layout': 'content-list',
            'title': 'Test',
            'body_paragraphs': [...],
            # ... 其他字段
        }
    ]
    
    result = _normalise_pptx(raw_slides)
    
    # 验证结果
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0]['type'], 'bullets')
    # ... 更多断言
```

### 添加回归测试用例

放置 PPTX 文件在 `tests/fixtures/` 中：

```bash
mkdir -p tests/fixtures
cp your_file.pptx tests/fixtures/
```

然后运行：

```bash
python tests/regression_test_pptx.py tests/fixtures/your_file.pptx --json
```

---

## 📈 性能基准

| 测试 | 耗时 | 内存 |
|------|------|------|
| 单元测试 (15 个) | < 1s | < 50MB |
| 回归测试 (单个 PPTX) | 1-5s | 50-200MB |
| 代码审查 | < 1s | < 20MB |
| 完整套件 | < 10s | < 300MB |

---

## 🎯 修复 vs 测试检查清单

### 修复内容丢失 bug 时：

- [ ] 移除任何 `[:N]` 截断操作
- [ ] 确保 `all_items` 完整传递
- [ ] 保留所有 `body_texts`
- [ ] 保留所有 `smartart_texts`
- [ ] 使用 `'\n'.join()` 分隔
- [ ] 验证无项被跳过或合并
- [ ] 运行 `pytest tests/test_normalise_pptx.py -v`
- [ ] 运行代码审查检查清单
- [ ] 对真实 PPTX 运行回归测试

### 代码审查时：

- [ ] 检查是否有 `[:N]` 截断
- [ ] 检查是否有 `[0]` 只取首项
- [ ] 检查是否有 `continue` / `break`
- [ ] 检查是否有 `return []` 
- [ ] 运行 `code_review_checklist.py --check file.py`
- [ ] 查看 HTML 报告

---

## 📞 常见问题

**Q: 单元测试失败，如何调试？**

A: 运行特定测试，查看详细输出：

```bash
pytest tests/test_normalise_pptx.py::TestNormalisePptxDataIntegrity::test_no_content_loss_in_bullets -vv
```

**Q: 回归测试显示内容丢失，怎么办？**

A: 检查 JSON 报告找出问题 slide，然后：

1. 查看生成的 HTML 文件
2. 对比原始 PPTX 提取的 JSON
3. 在 `test_normalise_pptx.py` 中添加单元测试重现问题
4. 修改 `generate_slides.py` 中的 `_normalise_pptx()` 函数
5. 重新运行回归测试验证修复

**Q: 如何在 CI 中自动运行这些测试？**

A: 参考上面的 "CI/CD 集成" 部分。

---

## 📝 测试维护

### 定期任务

- **每周**: 对新增 PPTX 文件运行回归测试
- **每次修改**: 运行完整测试套件 (`run_tests.py`)
- **重大改动**: 添加相应的单元测试
- **每月**: 审查测试覆盖率

### 测试用例库

建议在 `tests/fixtures/` 中保存代表性 PPTX 文件：

```
fixtures/
├── simple_bullets.pptx          # 简单列表
├── complex_table.pptx           # 复杂表格
├── many_items.pptx              # 100+ 项列表
├── mixed_content.pptx           # 混合内容
├── with_smartart.pptx           # SmartArt 内容
└── regression_001.pptx          # 之前的 bug 文件
```

---

## ✅ 验证清单

完成测试框架后，确认：

- [ ] 所有单元测试通过 (`pytest test_normalise_pptx.py -v`)
- [ ] 回归测试对已知 PPTX 文件通过
- [ ] 代码审查未检测到危险模式
- [ ] `run_tests.py` 可正常运行
- [ ] 文档清晰完整
- [ ] 有 HTML/JSON 报告生成
- [ ] 项目 README 中引用了测试文档

---

**更新时间**: 2025-03-19
**维护者**: PPTX 转换工具团队
