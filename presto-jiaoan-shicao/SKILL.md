---
name: presto-jiaoan-shicao
version: "1.0.0"
description: 将课程内容、教学设计、实训安排或项目化教学单元转换为 Presto 实操教案模板 Markdown 并生成横向 A4 PDF。当用户请求「实操教案」「实训教案」「教学活动设计」「职业教育教案」「项目化教学单元」「课程教案表」「把教学内容排成教案表」等时触发此技能。
---

# Presto Jiaoan Shicao

将课程材料、教学目标、实训任务或零散教学安排整理为 `jiaoan-shicao` 模板 Markdown，并编译为横向 A4 实操教案 PDF。

## 工作流程

```
输入材料 → 提炼教学结构 → 生成 jiaoan-shicao Markdown → 编译 PDF
```

### 步骤 1：分析输入

识别用户提供的是完整教案、课程大纲、实训任务、课堂活动草稿，还是零散素材。优先保留已有的课程名称、学习环节、学习单元、活动名称、课时、学习内容、学生活动、教师活动、教学方法与手段。

如果用户没有给出完整结构，按职业教育实操课的自然逻辑补全：

- 课程或项目主题 → `## 教学活动设计——课程主题`
- 学习阶段和训练目标 → `### 学习环节——学习单元`
- 课堂任务或训练步骤 → `#### 活动名称`
- 每段时长 → `##### 课时分配`
- 具体安排 → 四个内容块，依次为学习内容、学生活动、教师活动、教学方法与手段

### 步骤 2：生成 Markdown

必须写入 YAML front matter：

```yaml
---
template: "jiaoan-shicao"
---
```

标题层级必须按模板语义生成，不要改用普通 Markdown 表格：

| Markdown 输入 | 模板语义 |
|---|---|
| `## 教学活动设计——主题` | 居中章节标题；多个 `##` 自动另起一页 |
| `### 学习环节——学习单元` | 新建一张教学活动表 |
| `#### 活动名称` | “教学活动”列，模板自动编号 |
| `##### 0.5H` | “课时分配”列，并生成一行活动安排 |
| `#####` 后第 1 个内容块 | “学习内容”列 |
| `#####` 后第 2 个内容块 | “学生活动”列 |
| `#####` 后第 3 个内容块 | “教师活动”列 |
| `#####` 后第 4 个内容块 | “教学方法与手段”列 |

每个 `#####` 后尽量写满四个用空行分隔的内容块。前三个内容块可以多行，模板会自动编号；“教学方法与手段”建议保持短语或短句。

关于分页、`同上` 合并单元格、多活动、多表和常见错误，按需读取 [jiaoan-shicao-format.md](references/jiaoan-shicao-format.md)。

### 步骤 3：保存文件

按用户指定位置保存；未指定时保存在当前工作目录，建议使用 `YYYYMMDD 项目名` 子文件夹。Markdown 文件名使用教案主题，去掉不适合文件名的符号。

### 步骤 4：生成 PDF

使用 stdin/stdout 管道生成 PDF，不保留中间 `.typ` 文件。

macOS 本机：

```bash
cat "教案名.md" | /Users/mrered/.presto/templates/jiaoan-shicao/presto-template-jiaoan-shicao | typst compile - "教案名.pdf"
```

OpenClaw Linux：

```bash
PRESTO=/root/.openclaw/workspace/.presto/bin/presto-template-jiaoan-shicao
TYPST=/root/.openclaw/workspace/.bin/typst
DOC=/root/.openclaw/workspace/documents

cat "$DOC/项目文件夹/文件名.md" | "$PRESTO" | "$TYPST" compile --root /root/.openclaw/workspace - "$DOC/项目文件夹/文件名.pdf"
```

PDF 文件名与 Markdown 文件同名，扩展名改为 `.pdf`。

## 触发场景

此技能在以下场景自动触发：

1. **显式调用**：用户使用 `/presto-jiaoan-shicao` 或直接点名此技能。
2. **教案生成**：用户要求生成实操教案、实训教案、职业教育教案、课堂教学活动设计。
3. **结构转换**：用户要求把课程内容、实训任务、项目化教学单元排成教案表。
4. **模板编译**：用户要求使用 Presto `jiaoan-shicao` 模板生成 Markdown 或 PDF。

## 最小示例

```markdown
---
template: "jiaoan-shicao"
---

## 教学活动设计——PLC 基本指令应用

### 认识 PLC 硬件——了解 PLC 的基本组成与接线方法

#### 活动一：PLC 硬件认知

##### 0.5H

PLC 的基本组成：CPU 模块、输入模块、输出模块、电源模块。

观察实训台上的 PLC 设备，识别各模块位置及功能。

展示 PLC 实物，讲解各模块的功能与作用。

实物展示、讲练结合
```
