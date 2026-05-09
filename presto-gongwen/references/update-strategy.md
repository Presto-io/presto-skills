# 技能在线更新与自动更新策略

本文记录 `presto-gongwen` 技能从“手动复制更新”升级到“在线更新/自动更新”的可落地路线。

## 现状

当前技能安装链路已经具备在线更新的基础：

- `presto-skills` 仓库支持 `npx --yes skills add Presto-io/presto-skills --skill presto-gongwen -g -y` 安装。
- `npx skills` 已提供 `skills update [skills...]` 命令，可把已安装技能更新到最新版本。
- 仓库已有 `scripts/build_registry.py`，能生成 `registry.json` 并由 CI 发布到 CDN。
- 本地 `skills-lock.json` 记录了技能来源和内容哈希，可用于判断安装版本是否发生变化。

限制也很明确：

- 仅靠 `registry.json` 还不等于自动更新；安装端必须主动检查并替换本地技能。
- 当前 registry 需要使用技能自身的 `version`，不能长期写死 `1.0.0`。
- 自动更新必须避免覆盖用户本地改动，至少要先区分“官方安装目录”和“用户手工修改目录”。

## 推荐路线

### 第一阶段：手动在线更新

面向所有用户提供最小可用方案：

```bash
npx --yes skills update presto-gongwen -g -y
```

适用场景：

- 用户知道自己要更新。
- 更新频率低。
- 可以接受更新后重启 Codex/OpenClaw/Claude Code 等客户端。

发布侧要求：

- 合并 PR 到 `Presto-io/presto-skills/main`。
- CI 生成最新 `registry.json`。
- README 明确安装和更新命令。

### 第二阶段：半自动更新

在用户机器或 NAS/OpenClaw 上配置定时任务，每天或每周执行一次更新命令。

macOS `launchd`、Linux `cron`、OpenClaw 容器内定时任务均可使用同一条核心命令：

```bash
npx --yes skills update presto-gongwen -g -y
```

建议：

- 先记录更新日志，便于排查。
- 更新后提示用户重启相关客户端。
- 对 OpenClaw 这类长期运行环境，可安排在凌晨低峰期。

### 第三阶段：Presto 技能商店内置更新

如果 Presto 桌面端要做技能商店，建议复用模板更新的设计：

1. 启动或进入技能页时拉取技能 registry。
2. 读取本地安装清单（来源、版本、哈希、安装路径）。
3. 对比 registry 中的 `version` 或 `computedHash`。
4. 显示“可更新”状态，用户点击后执行更新。
5. 更新采用临时目录下载、校验、原子替换，失败时保留旧版本。

这是最稳的“在线更新”：用户可见、可控、可回滚。

### 第四阶段：静默自动更新

仅建议用于 official/trusted 技能，并满足以下条件：

- registry 中提供 `version`、`hash`、`source`、`path`、`trust`。
- 本地安装清单记录上次安装哈希。
- 本地技能目录没有用户手工修改，或用户明确开启“自动覆盖官方技能”。
- 下载后先校验哈希，再原子替换。
- 失败时不影响旧版本，日志可查。

推荐默认策略：

- official 技能可默认自动检查，但更新前给一次授权开关。
- community 技能只提示更新，不静默替换。
- 本地被用户修改过的技能只提示冲突，不覆盖。

## Registry 字段建议

`registry.json` 中每个技能建议包含：

```json
{
  "name": "presto-gongwen",
  "displayName": "Presto 公文排版",
  "description": "...",
  "version": "1.2.0",
  "author": "Presto-io",
  "repo": "Presto-io/presto-skills",
  "path": "presto-gongwen",
  "license": "MIT",
  "category": "productivity",
  "keywords": ["presto", "document", "formatting", "gongwen"],
  "trust": "official",
  "hash": "sha256:..."
}
```

其中：

- `version` 用于用户可读的更新判断。
- `hash` 用于安全校验和检测本地漂移。
- `repo` + `path` 用于 `npx skills` 或 Presto 自己的安装器下载源码。

## 对当前仓库的改造建议

短期需要做两件事：

1. 在 `SKILL.md` frontmatter 中维护 `version` 字段。
2. 让 `scripts/build_registry.py` 从 frontmatter 读取 `version`，并计算技能目录内容哈希写入 registry。

随后就可以做到：

- 手动：`npx skills update presto-gongwen -g -y`。
- 半自动：cron/launchd 定时执行更新命令。
- 产品化：Presto 读取 registry 后显示“可更新”并一键更新。
- 自动化：官方技能在用户授权后静默校验和替换。

## 风险与边界

- 技能是代理行为说明，自动更新等同于更新代理执行规则；必须把来源、信任级别和变更记录做清楚。
- 不建议让技能文件自己在运行时修改自己；这会让行为不可审计。
- 真正的自动更新应由外层工具（`npx skills`、Presto 桌面端、OpenClaw 定时任务）执行，而不是由技能提示词执行。
- 更新后多数客户端需要重启或重新加载技能，才能读取新的 `SKILL.md`。
