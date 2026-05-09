---
name: presto-gongwen
version: "1.2.0"
description: 将任意文档转换为符合公文模板规范的 Markdown 并生成 PDF。支持纯文本、Markdown、Word、PDF 等输入格式。当用户请求「转换成公文格式」「生成公文」「帮我写报告」「整理成文档」「工作总结」「会议纪要」「通知」「发言稿」等时触发此技能。
---

# Presto Gongwen

将任意文档转换为符合 GongWen-Template-Lite（类公文模板）规范的 Markdown 文件，并自动生成 PDF。

## 工作流程

```
输入文档 → 分析提取 → 生成 Markdown → 编译 PDF
```

### 步骤 1：分析输入

根据输入类型执行相应操作：

| 输入类型 | 处理方式 |
|---------|---------|
| 纯文本/对话 | 直接进入步骤 2 |
| Markdown 文件 | 读取后分析结构 |
| Word 文档 | 使用文档处理能力提取内容 |
| PDF 文档 | 使用 PDF 处理能力提取文本 |

同时判断运行环境：

| 环境 | 工作区 | 适用命令 |
|-----|--------|----------|
| macOS 本机 | 当前工作目录或用户指定目录 | `/Users/mrered/.presto/templates/gongwen/presto-template-gongwen` + `typst` |
| OpenClaw Linux | `/root/.openclaw/workspace` | `/root/.openclaw/workspace/.presto/bin/presto-template-gongwen` + `/root/.openclaw/workspace/.bin/typst` |

### 步骤 2：提取元数据

自动从原文档推断以下信息：

- `title`: 从文档标题或内容主题推断，选择简短恰当的标题。
  - 优先使用原文档的主标题（非副标题）。
  - 短标题（20 字以内）不要加 `|`，直接写纯文本。
  - 只有标题确实过长需要视觉换行时才使用 `|` 在语义断点分隔，如 `"项目名称|建设项目立项书"`。
  - 不要使用反斜杠换行。
  - 如果文档有明确标题（如报告、发言稿、会议纪要），YAML `title` 已经承载标题，正文中不要再用 `##` 重复写一遍标题。
- `author`: 从文档署名、文件属性推断，默认为空；可写字符串或作者列表。
- `date`: 使用当前日期（YYYY-MM-DD 格式）。
- `signature`: 根据文档类型判断，报告、申请、通知、正式函件通常设为 `true`；笔记、学习心得、材料摘编类通常设为 `false`。`signature: true` 时作者和日期生成文末右侧落款；`signature: false` 时作者显示在标题下方。
- `template`: 明确写 `template: "gongwen"` 指定模板。

### 步骤 3：转换内容

按照公文模板规范重构内容：

1. **标题层级映射**（模板自动编号，无需手动添加序号）
   - 原一级标题 → 删除（使用 YAML `title`）。
   - 原二级标题 → `##`（模板自动编号：一、二、三...）。
   - 原三级标题 → `###`（模板自动编号：（一）（二）...）。
   - 原四级标题 → `####`（模板自动编号：1. 2. 3...）。
   - 原五级标题 → `#####`（模板自动编号：（1）（2）...）。
   - 不要手动添加编号，如“一、”“（一）”“1.”。
   - 如果原文标题自带数字编号（如 `1.1`、`2.2`），去掉数字前缀，只保留标题文本。

2. **段落处理**
   - 正文自动首行缩进。
   - 列表保持语义，但可规范化标点和层级。
   - 特殊格式使用 `{.noindent}` 或 `::: {.noindent}`。
   - 复杂 ASCII 框图、字符图、艺术化流程图应转换为列表、步骤说明或表格，避免保留不可渲染符号。
   - 笔记、发言稿、学习心得类文档不要套用“以上报告，请审阅”等报告式收尾。
   - 模板会自动转换常见中文标点；生成 Markdown 时仍应主动使用规范中文标点，不依赖模板兜底。

3. **图片处理**
   - 图片放在 Markdown 同目录或可被 `typst --root` 访问的工作区路径下。
   - 图片前后都应有足够文字，形成“文字-图片-文字”的三明治结构，避免图片独占半页后出现大段留白。
   - OpenClaw 管道编译时，图片路径使用相对于工作区根目录的路径，如 `![说明](documents/20260510 项目名/图片名.png)`。
   - 本机直接编译时，可使用相对于 Markdown 文件的路径。
   - 单张图片自动居中并限制在版心内，图题主要取图片文件名（不含扩展名），所以图片文件名要清楚。
   - 多张图片分别编号：每张图片单独成段。
   - 多图连续放置在同一段会并排显示；多图都写相同 alt text 时组成子图组合，alt text 作为总图题，文件名作为子图小标题。
   - 如需 AI 生图，优先使用现有图片生成技能或用户提供的生图服务；生成后把图片放入项目文件夹，并在正文中前后补足说明文字。

4. **表格处理**
   - 表格必须有表头行（分隔线 `|---|` 上方的那行），不能只有数据行没有表头。
   - 保留表格结构，根据内容自动判断对齐方式：
     - 纯数字、日期、金额列 → 右对齐 `---:`
     - 短文本（少于 5 字）→ 居中 `:---:`
     - 长文本、描述性内容 → 左对齐 `:---`
   - 表格内换行使用 `<br>` 标签。
   - 表格后添加 `: 表格标题` 自动生成“表 n 表格标题”编号。
   - 表题必须紧跟在表格后面；不要手写“表 1”。
   - 长表格可自然跨页，后续页会重复表头，并显示续表标题。
   - 表格也遵循三明治原则：表格前有引入，表格后有解释或过渡。

### 步骤 4：生成 Markdown

**项目文件夹**：

- OpenClaw：在 `/root/.openclaw/workspace/documents/` 下创建 `YYYYMMDD 项目名` 格式的子文件夹，日期和项目名之间用空格。
- macOS 本机：按用户指定位置保存；未指定时保存到当前工作目录，可同样使用 `YYYYMMDD 项目名` 子文件夹。

**文件命名规则**：直接使用文档标题作为文件名（去除 `|` 换行符）。

```yaml
# 标题: "知识图谱学习系统|建设项目立项书"
# 文件名: 知识图谱学习系统建设项目立项书.md
```

对于输入中含有手工编号的小节、非标准字符图或复制粘贴残留格式，优先生成清晰可读的正文结构，不将原始编号/图字符直接带入最终 Markdown。

### 步骤 5：生成 PDF

使用 stdin/stdout 管道生成 PDF，不保留中间 `.typ` 文件。

macOS 本机：

```bash
cat "标题名.md" | /Users/mrered/.presto/templates/gongwen/presto-template-gongwen | typst compile - "标题名.pdf"
```

OpenClaw Linux：

```bash
PRESTO=/root/.openclaw/workspace/.presto/bin/presto-template-gongwen
TYPST=/root/.openclaw/workspace/.bin/typst
DOC=/root/.openclaw/workspace/documents

cat "$DOC/项目文件夹/文件名.md" | "$PRESTO" | "$TYPST" compile --root /root/.openclaw/workspace - "$DOC/项目文件夹/文件名.pdf"
```

OpenClaw 管道编译时 `--root /root/.openclaw/workspace` 是必须项；图片路径应写成 `documents/子文件夹/图片名.png`。

**PDF 文件名**：与 Markdown 文件同名，扩展名改为 `.pdf`。

**常见模板路径**：

- macOS gongwen：`/Users/mrered/.presto/templates/gongwen/presto-template-gongwen`
- OpenClaw gongwen：`/root/.openclaw/workspace/.presto/bin/presto-template-gongwen`
- OpenClaw jiaoan-shicao：`/root/.openclaw/workspace/.presto/bin/presto-template-jiaoan-shicao`

## 格式规范速查

详细的格式规范请参考 [gongwen-format.md](references/gongwen-format.md)。

关于在线更新和自动更新设计，请参考 [update-strategy.md](references/update-strategy.md)。

### YAML Front-Matter 模板

```yaml
---
title: "文档标题"
author:
  - "作者名"
date: "2026-04-04"
signature: true
template: "gongwen"
---
```

**title 换行规则**：短标题（20 字以内）直接写纯文本；只有标题确实过长需要视觉换行时才用 `|` 分隔，如 `"知识图谱学习系统|建设项目立项书"`。

### 常用格式标记

| 效果 | 语法 |
|-----|------|
| 无缩进段落 | `::: {.noindent}` 包裹 |
| 无缩进行内 | `文本{.noindent}` |
| 空 1 行 | `{v}` 独立成段 |
| 空 N 行 | `{v:N}` 独立成段 |
| 强制分页 | `{pagebreak}` |
| 弱分页 | `{pagebreak:weak}` |

### 表格格式

标准 Markdown 表格必须有表头行。在表格后使用 `: 表格标题` 会自动生成“表 n 表格标题”编号。

**示例**（编译后自动显示为“表 1 检查工作进度安排”）：

```markdown
| 阶段 | 时间 | 负责部门 |
|:-----|-----:|:---------|
| 自查自纠 | 3月1日-15日 | 各部门 |
| 集中检查 | 3月16日-31日 | 安全管理处 |

: 检查工作进度安排
```

### 称呼与落款

```markdown
各位领导：

[正文内容]

以上报告，请审阅。
```

报告、申请类可使用报告式收尾；通知、纪要、笔记、发言稿、学习心得类应按文体自然收束。

## 触发场景

此技能在以下场景自动触发：

1. **显式调用**：用户使用 `/presto-gongwen` 命令。
2. **写作请求**：「帮我写个报告」「整理成文档」「生成工作总结」。
3. **场景关键词**：提及「会议纪要」「通知」「报告」「公文」「发言稿」等。
4. **格式转换**：用户要求转换文档为公文/正式格式。

## 完整示例

输入（纯文本）：

```text
项目进度报告

张三
2026年4月4日

项目进展顺利，主要完成了以下工作：
1. 完成需求分析
2. 设计方案确定
3. 开始编码实现

下一步计划：
继续推进开发工作
```

输出（`项目进度报告.md`）：

```markdown
---
title: "项目进度报告"
author:
  - "张三"
date: "2026-04-04"
signature: true
template: "gongwen"
---

各位领导：

现将项目进展情况报告如下：

## 工作进展

1. 完成需求分析；
2. 设计方案确定；
3. 开始编码实现。

## 下一步计划

继续推进开发工作。

以上报告，请审阅。
```
