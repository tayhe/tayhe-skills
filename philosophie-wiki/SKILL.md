---
name: philosophie-wiki
description: |
  哲学知识库维护技能。遵循 Karpathy LLM Wiki 方法论，以运动为中心组织哲学知识。
  支持多位哲学家共存，每位哲学家定义自己的运动类型（Bewegungstyp）。
  三个核心操作：Ingest（摄入新文献）、Query（查询与沉淀）、Lint（健康审查）。
  触发词：「摄入」「ingest」「查询wiki」「lint」「知识库维护」「wiki健康检查」「处理文献」「阅读笔记」「帮我把这本书的笔记做进去」「知识库里关于X有什么」。
  当用户要求处理新文献、查询知识库、检查知识库健康状态、或将讨论结果沉淀为笔记时使用。
---

# Philosophie-Wiki · 哲学知识库维护

以运动为中心的哲学知识库操作指南。支持多位哲学家共存，每位哲学家定义自己的运动类型。遵循 Karpathy 的 LLM Wiki 方法论——wiki 是持久的、复利增长的产物，LLM 负责维护，人类负责策展和提问。

## 前置条件

执行任何操作前，先读取目标知识库的 `AGENTS.md` 了解其具体目录结构、运动类型定义和约定。标准路径格式：`~/Documents/Philosophie-studien/`

## 知识库标准结构

每位哲学家使用相同的五层结构，但运动类型（Bewegungstyp）因哲学家而异：

```
{知识库根目录}/
├── AGENTS.md
├── Raw/
│   ├── Primärquellen/{哲学家名}/   # 一手文献（只读）
│   └── Sekundärliteratur/{作者名}/ # 二手研究（只读）
├── Wiki/
│   ├── {哲学家名}/                 # 每位哲学家独立目录
│   │   ├── Begriffe/               # 概念笔记
│   │   ├── Bewegungen/             # 运动笔记（中心层，运动类型因人而异）
│   │   ├── Momente/                # 环节笔记
│   │   ├── Spannungen/             # 张力笔记
│   │   └── Anwendungen/            # 应用笔记
│   └── Studien/{Autor-Werk}/       # 二手文献研究
│       ├── Lesenotizen.md
│       ├── Kernthesen.md
│       └── Verbindungen.md
└── _index/
    ├── index.md
    └── log.md
```

## 运动类型（Bewegungstypen）

不同哲学家有不同的运动形态。"运动"不必是黑格尔式的辩证运动。

| 哲学家 | Bewegungstyp | 运动特征 | 核心逻辑 |
|--------|-------------|---------|----------|
| Hegel | Dialektik | 概念通过内在矛盾自我发展 | 正题→反题→合题→更高综合 |
| Plato | Anabasis | 从意见到知识的上升 | 意见→困惑→回忆→直观理念 |
| Kant | Transzendentalbewegung | 知性到理性的过渡与二律背反 | 感性→知性→理性→二律背反 |
| Wittgenstein | Sprachspielwechsel | 语言规则的跳跃 | 用法→规则→界限→新用法 |
| Nietzsche | Perspektivenwechsel | 价值重估的动态过程 | 旧价值→怀疑→重估→新价值 |

## 五层笔记关系

```
Begriffe（概念）←→ Bewegungen（运动）←→ Momente（环节）
       ↑                    ↑                    ↑
       └──────── Spannungen（张力）──────────────┘
                         ↑
                  Anwendungen（应用）
```

运动笔记是中心：展开为环节，关联概念。环节上溯运动并关联概念。张力与运动/概念/环节双向引用。应用引用运动、概念、张力。

---

## 操作一：Ingest（摄入）

触发：「处理这篇文献」「ingest这个」「读一下这本书」「帮我把笔记做进去」

### 流程

1. **确认资料** — 类型（一手/二手）？位置（已在 Raw/ 或需复制）？格式（PDF需提取文本）？
2. **阅读讨论** — 读取资料，与用户讨论关键要点。识别涉及的：概念（Begriffe）、运动（Bewegungen）、环节（Momente）、张力（Spannungen）
3. **创建/更新页面** — 按顺序：概念→运动→环节→张力→应用→更新现有页面。每创建一个页面，立即更新所有相关页面的 `[[]]` 引用。注意：frontmatter 中必须包含 `Philosoph` 字段标识所属哲学家，运动笔记必须包含 `Bewegungstyp` 字段。
4. **更新索引** — 更新 `_index/index.md`，追加 `_index/log.md`
5. **自检** — frontmatter 完整？双向引用正确？环节链表连续？索引已更新？

### 页面创建顺序

```
① Begriffe（如有新概念）
② Bewegungen（如有新运动）
③ Momente（为运动的每个阶段创建）
④ Spannungen（如有新张力）
⑤ Anwendungen（如有应用场景）
⑥ 更新受影响的现有页面引用
```

### 二手文献研究笔记

在 `Wiki/Studien/{Autor-Werk}/` 下创建三个文件：
- `Lesenotizen.md` — 逐章阅读笔记
- `Kernthesen.md` — 核心论点（3-7个）
- `Verbindungen.md` — 与已有概念/运动的关联

---

## 操作二：Query（查询与沉淀）

触发：「黑格尔怎么看X？」「知识库里关于Y有什么？」「帮我查一下wiki」

### 流程

1. **搜索** — 读 `_index/index.md` 找相关页面，读取及其关联页面
2. **回答** — 基于 wiki 内容回答，带引用来源。形式：口头回答 / Markdown页面 / 对比表格 / Mermaid图表
3. **沉淀（可选）** — 好的回答回存为新页面：概念对比、张力深入探讨、新应用场景、综合分析。简单引用不沉淀，新综合才沉淀。沉淀时遵循 Ingest Step 3-5

---

## 操作三：Lint（健康审查）

触发：「lint一下」「检查知识库健康状态」「wiki有没有问题？」

### 检查清单

**结构完整性**：
- [ ] 每个运动笔记至少有一个环节笔记？
- [ ] 环节笔记的前驱/后继链接正确？
- [ ] 环节笔记有关联的概念笔记？
- [ ] 概念笔记有运动笔记的支撑（`stützt_auf`）？

**引用一致性**：
- [ ] 所有 `[[]]` 引用指向存在的文件？（无死链接）
- [ ] 无孤立页面（无入站链接）？
- [ ] 双向引用一致？（A→B 则 B→A）

**Frontmatter 规范**：
- [ ] `type` / `layer` 字段正确？
- [ ] 环节笔记 `Position` 连续？
- [ ] 环节笔记链表 `vorheriges_Moment` / `nächstes_Moment` 正确？

**内容质量**：
- [ ] 概念笔记有"规定"（Bestimmung）而非只是定义？
- [ ] 运动笔记展示完整辩证过程？
- [ ] 张力笔记包含"尝试的调和"和"当前状态"？

**索引一致性**：
- [ ] `_index/index.md` 与实际页面一致？
- [ ] `_index/log.md` 记录所有 ingest？

### 输出

```
┌─────────────────────┬────────┬──────────────────────────┐
│ 检查项              │ 状态   │ 备注                     │
├─────────────────────┼────────┼──────────────────────────┤
│ 运动→环节完整性     │ ✓/✗    │                          │
│ 环节链接连续性      │ ✓/✗    │                          │
│ 死链接              │ ✓/✗    │ 找到 N 个                │
│ 孤立页面            │ ✓/✗    │ 找到 N 个                │
│ Frontmatter 规范    │ ✓/✗    │ N 个需修复               │
│ 索引一致性          │ ✓/✗    │                          │
└─────────────────────┴────────┴──────────────────────────┘
```

发现问题时提出修复建议，修复前与用户确认。

---

## 命名约定

- 所有目录名和文件名使用**德语**
- 名词**首字母大写**（德语名词大写规则）
- 概念笔记：概念原名（`Sittlichkeit.md`）
- 运动笔记：描述运动的短语（`ethische-Substanz.md`）
- 环节笔记：描述内容的短语（`ethische-Substanz-als-Einheit.md`）
- 张力笔记：描述张力的短语（`Individuum-und-Substanz.md`）
- 应用笔记：描述场景的短语（`moderne-ethische-Konflikte.md`）
- 二手文献：`Autor-Werk/`（`Kojève-Einführung-Hegel/`）

## 扩展规则

**添加哲学家**：在 AGENTS.md 中定义 Bewegungstyp → 在 `Wiki/` 下建目录 → 创建五层子目录 → 在 `Raw/Primärquellen/` 下建目录 → 更新索引

**添加二手文献**：在 `Raw/Sekundärliteratur/` 下建目录 → 放入文献 → 在 `Wiki/Studien/` 下建研究目录（Lesenotizen/Kernthesen/Verbindungen）→ 更新索引和日志

---

## 错误预防

| 错误 | 预防 |
|------|------|
| 忘记双向引用 | 每创建页面立即更新相关页面 |
| Frontmatter 遗漏 | 创建后对照参考文件验证 |
| 环节链表断裂 | 创建时同时更新前驱和后继 |
| 概念缺运动支撑 | 记录 `stützt_auf` 字段 |
| 索引未更新 | ingest 最后一步固定更新索引 |

## 参考资料

- **笔记模板与 Frontmatter 规范**：详见 [references/note-templates.md](references/note-templates.md)
- **详细 Frontmatter 字段规格**：详见 [references/frontmatter-spec.md](references/frontmatter-spec.md)
