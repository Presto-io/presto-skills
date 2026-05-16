---
name: presto-jiaoan-jihua
version: "1.0.2"
description: 将课程安排、教学任务、学习环节或零散教学内容转换为 Presto `jiaoan-jihua` 授课进度计划表 Markdown，并生成 A4 PDF。当用户请求「授课计划」「教学进度计划」「课程进度表」「周次安排」「排课时」「把教学内容排成授课进度表」等时触发此技能。
---

# Presto Jiaoan Jihua

将课程元数据、学习任务、学习环节和教学内容整理为 Presto `jiaoan-jihua` 模板 Markdown，生成“工学一体化课程/基本技能课程授课进度计划表”，并编译为 A4 PDF。模板契约以 `presto-official-templates/jiaoan-jihua` 1.0.2 为准。

## 工作流程

```
输入材料 → 提炼课程事实 → 生成授课进度 Markdown → 编译 PDF
```

### 步骤 1：分析输入

识别用户提供的是完整授课计划、课程大纲、项目任务列表、周次课时安排，还是零散教学内容。先提取用户明确给出的课程事实，包括专业名称、课程名称、授课教师、授课班级、首次授课日期、学习任务、学习环节、教学内容和课时。

材料不完整时仍然输出最小完整骨架。补全采用保守策略：

- 可直接推断的课程名称、学习任务名、学习环节名、教学内容和课时，可以补入正文。
- 不确定的 `major_name`、`teacher_name`、`class_name` 留空。
- 不确定的 `first_teaching_day` 可以留空；如果用户要求立即排程且未给日期，使用当前日期作为排程起点，并说明这是排程起点假设。
- 不虚构学校名称、专业、班级、教师姓名或开课日期。

### 步骤 2：生成 YAML Front-Matter

必须写入 YAML Front-Matter。只写最小字段，学年、学期、周次范围、制表人、每日课时和校历由模板推断：

```yaml
---
major_name: "电气自动化技术"
course_name: "电气设备控制线路安装与调试"
teacher_name: "张老师"
class_name: "29WG电气3"
first_teaching_day: "2026-03-06"
template: "jiaoan-jihua"
---
```

字段顺序固定为：`major_name`、`course_name`、`teacher_name`、`class_name`、`first_teaching_day`、`template`。

`first_teaching_day` 无法解析时，模板会回退到内置校历或运行时默认日历。旧输入中的 `calendar_json` 仍兼容，但不要主动向用户索要日历路径。

### 步骤 3：生成学习任务与学习环节

正文只使用三层结构：

```markdown
## 学习任务名称

### 学习环节名称

教学内容-课时
教学内容-课时
```

模板语义：

| Markdown 输入 | 模板语义 |
|---|---|
| `## 学习任务名称` | 新建学习任务行，模板自动编号为“学习任务1名称” |
| `### 学习环节名称` | 新建学习环节，模板自动编号为“学习环节1名称” |
| `教学内容-4` | 一行教学内容，学时列显示 `4` |
| `教学内容` | 未写课时时默认 `2` |

每个 `##` 下至少保留一个 `###`，每个 `###` 下至少保留一条教学内容。课时必须使用正整数，不要写 `0.5`、`2H` 或 `2课时`；模板识别的稳定写法是 `教学内容-2`。

### 步骤 4：排程与日历

模板根据 `first_teaching_day`、内置校历和默认每日 8 课时自动计算学年、学期、周次、星期和学时：

- `first_teaching_day` 使用 `YYYY-MM-DD`。
- 每天默认排 8 课时。
- 内置校历的第一天用于推断学年和学期；上半年为第二学期，学年为前一年到今年；下半年为第一学期，学年为今年到下一年。
- 周次范围由实际排课结果自动推断。
- 兼容旧输入中的外部日历；外部日历 JSON 解析失败或日期格式无效时，PDF 中会显示“日历文件解析失败，已使用默认日历”。
- 单条教学内容跨多天或跨周时，模板会在同一行合并显示多个周次和星期，多个值用空格分隔。

### 步骤 5：保存文件

按用户指定位置保存；未指定时保存在当前工作目录，建议使用 `YYYYMMDD 项目名` 子文件夹。Markdown 文件名使用课程名或授课计划主题，去掉不适合文件名的符号。

### 步骤 6：生成 PDF

使用 stdin/stdout 管道生成 PDF，不保留中间 `.typ` 文件。

macOS 本机：

```bash
cat "授课计划.md" | /Users/mrered/.presto/templates/jiaoan-jihua/presto-template-jiaoan-jihua | typst compile - "授课计划.pdf"
```

OpenClaw Linux：

```bash
PRESTO=/root/.openclaw/workspace/.presto/bin/presto-template-jiaoan-jihua
TYPST=/root/.openclaw/workspace/.bin/typst
DOC=/root/.openclaw/workspace/documents

cat "$DOC/项目文件夹/文件名.md" | "$PRESTO" | "$TYPST" compile --root /root/.openclaw/workspace - "$DOC/项目文件夹/文件名.pdf"
```

PDF 文件名与 Markdown 文件同名，扩展名改为 `.pdf`。

关于 YAML Front-Matter、日历 JSON、正文结构、多任务、多环节和常见错误，按需读取 [jiaoan-jihua-format.md](references/jiaoan-jihua-format.md)。

## 触发场景

此技能在以下场景自动触发：

1. **显式调用**：用户使用 `/presto-jiaoan-jihua` 或直接点名此技能。
2. **授课计划生成**：用户要求生成授课计划、教学进度计划、课程进度表、周次安排表。
3. **结构转换**：用户要求把课程大纲、项目任务、学习任务或教学内容排成授课进度表。
4. **模板编译**：用户要求使用 Presto `jiaoan-jihua` 模板生成 Markdown 或 PDF。

## 最小示例

```markdown
---
major_name: "电气自动化技术"
course_name: "电气设备控制线路安装与调试"
teacher_name: "张老师"
class_name: "29WG电气3"
first_teaching_day: "2026-03-06"
template: "jiaoan-jihua"
---

## CA6140卧式车床电气控制线路安装与调试

### 安技教育及旧知识回顾

安技教育-1
安技教育及旧知识回顾-1
常用低压电器元件知识回顾，万用表的使用方法回顾-1

### CA6140卧式车床电气控制线路识读

CA6140卧式车床主电路识读-4
CA6140卧式车床控制电路识读-4
常见电气故障现象分析-2

## X62W万能铣床电气控制线路安装与调试

### X62W万能铣床电气控制线路识读

X62W万能铣床主电路识读-4
X62W万能铣床控制电路识读-4
```
