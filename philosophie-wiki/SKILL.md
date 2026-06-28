---
name: philosophie-wiki
description: |
  哲学知识库维护技能。遵循 Karpathy LLM Wiki 方法论，核心原则：文本结构优先，辩证法为注释原则。
  支持多位哲学家共存，每位哲学家按原书结构组织知识库（章>节>小节>环节）。
  三个核心操作：Ingest（摄入新文献）、Query（查询与沉淀）、Lint（健康审查）。
  触发词：「哲学知识库」「知识库摄入」「ingest」「查询wiki」「lint」「知识库维护」「wiki健康检查」「处理文献」「阅读笔记」「帮我把这本书整理出笔记」「知识库里关于X有什么」。
  当用户要求处理新文献、查询知识库、检查知识库健康状态、或将讨论结果沉淀为笔记时使用。
---

# Philosophie-Wiki · 哲学知识库维护

以**文本结构优先**为原则的哲学知识库操作指南。支持多位哲学家共存，目录结构与原书结构一一对应。辩证法在注释（`## 思辨注释`）中体现，而非在目录结构中强加。

遵循 Karpathy 的 LLM Wiki 方法论——wiki 是持久的、复利增长的产物，LLM 负责维护，人类负责策展和提问。

**规范来源**：本 Skill 仅包含通用操作程序和 Frontmatter 检查清单。所有具体规范（目录结构、命名规则、Frontmatter、操作流程）均以 `{知识库根目录}/AGENTS.md` 为唯一事实来源，各著作特有的结构参数（OCR路径、原书目录、术语翻译）查阅对应的 `{原著名}-Ingest-Leitfaden.md`。

## 前置条件

执行任何操作前，先读取目标知识库的 `AGENTS.md` 和 `{哲学家目录}/{原著名}/Ingest-Leitfaden.md`（如有）了解其具体结构和约定。标准路径格式：`~/Documents/Philosophie-studien/`

## 知识库标准结构

**核心原则：目录结构与原书结构一一对应。**

完整结构规范见 `{知识库根目录}/AGENTS.md`，本 Skill 仅提供操作接口。

| 章 | 是否有节 | 节结构 |
|---|---|---|
| I. Die sinnliche Gewißheit | 无 | 直接有小节 |
| II. Die Wahrnehmung | 无 | 直接有小节 |
| III. Krafft und Verstand | 无 | 直接有小节 |
| IV. Die Wahrheit der Gewißheit seiner selbst | **有** | A (Anerkennung), B (Freyheit) |
| V. Gewißheit und Wahrheit der Vernunft | 有 | A, B, C |
| VI. Der Geist | **有** | A (Sittlichkeit), B (Bildung), C (Moralität) |
| VII. Die Religion | 有 | A, B, C |
| VIII. Das absolute Wissen | 无 | 直接有小节 |

---

## 四级文件命名规范

| 层级 | 文件类型 | 命名规则 | 示例 |
|------|---------|---------|------|
| **Kapitel** | 章总述 | `{章号}-{章名}.md`（在章目录下） | `V-Vernunft.md` |
| **Abschnitt** | 节总述 | `{节名}.md`（在节目录内） | `A-Beobachtende-Vernunft.md` |
| **Unterabschnitt** | 小节页 | `{小节名}.md`（**在小节目录内**） | `a-Beobachtung-der-Natur.md` |
| **Momente** | 环节文件 | `{环节名}.md`（在环节目录内） | `α-Beziehung-auf-das-Unorganische.md` |

**命名规则**：
- 所有文件名使用**原著语言**（黑格尔用德语）
- **名词首字母大写**，复合词用连字符 `-` 连接
- **节标题使用原书完整标题**——如 `A-Der-wahre-Geist-die-Sittlichkeit` 而非简写
- **环节使用原书标题**——希腊字母（α/β/γ）或德语词（如 `γγ-Das-Aeussere-selbst-als-Innres`），不用 `A.a.1.1` 数字编号

---

## 操作一：Ingest（摄入）

触发：「处理这篇文献」「ingest这个」「读一下这本书」「帮我把笔记做进去」

### 流程

1. **确认资料** — 类型（一手/二手）？位置（已在 Raw/ 或需复制）？格式？
2. **确认原书结构** — 读取 AGENTS.md 和该著作的 Ingest-Leitfaden，确认章/节/小节边界
3. **阅读讨论** — 读取资料，与用户讨论关键要点。识别：环节划分（Momente）、核心辩证运动、扬弃关系
4. **创建/更新页面** — 按顺序：章总述 → 节总述 → 小节页 → 环节文件。**小节页文件必须放在对应的小节目录内**
5. **补充注释** — 每个层级的文件必须包含 `## 思辨注释`，以辩证法阐述概念运动
6. **更新索引** — 更新 `_index/index.md`，追加 `_index/log.md`

### 页面创建顺序

```
① 章总述（Kapitel-Übersicht）
② 节总述（Abschnitt-Übersicht）——在节目录内
③ 小节页（Unterabschnitt）——**在小节目录内**
④ 环节文件（Momente）——在小节目录的子目录内
⑤ 更新相关页面的引用
⑥ 更新索引
```

### Frontmatter 规范（必须字段）

**章总述**：
```yaml
---
title: "V. Gewißheit und Wahrheit der Vernunft"
chapter: "V-Vernunft"
Position: "V"
GW.9: "P132–P240"
---
```

**节总述**：
```yaml
---
title: "A. Der wahre Geist, die Sittlichkeit"
chapter: "VI-Geist"
abschnitt: "A"
Position: "VI.A"
GW.9: "P240–P264"
---
```

**小节页**：
```yaml
---
title: "a. Die sittliche Welt, das menschliche und göttliche Gesetz"
chapter: "VI-Geist"
abschnitt: "a"
Position: "VI.A.a"
GW.9: "P241–P251"
---
```

**环节文件**：
```yaml
---
title: "A.a.1.1 Die Gewißheit der Vernunft"
chapter: "V-Vernunft"
abschnitt: "A"
unterabschnitt: "a"
Position: "A.a.1.1"
vorheriges: "IV.B.c-Unglückliches-Bewußtsein"
nächstes: "A.a.1.2"
GW.9: "P132–P140"
---
```

### 思辨注释的内容要求

每个层级的文件必须包含 `## 思辨注释`（Spekulative Anmerkung），阐述：
- **an sich / für sich / an und für sich**（自在/自为/自在自为）
- 本阶段与前一阶段的扬弃关系
- 本阶段内部矛盾的运动方向
- 本阶段向下一阶段的过渡逻辑

---

## 操作二：Query（查询与沉淀）

触发：「黑格尔怎么看X？」「知识库里关于Y有什么？」「帮我查一下wiki」

### 流程

1. **搜索** — 读 `_index/index.md` 找相关页面，读取相关页面及其引用页面
2. **回答** — 基于 wiki 内容回答，带引用来源。形式：口头回答 / Markdown页面 / 对比表格 / Mermaid图表
3. **沉淀（可选）** — 好的回答回存为新页面：概念对比、张力深入探讨、新应用场景、综合分析。简单引用不沉淀，新综合才沉淀。沉淀时遵循 Ingest Step 3-6

---

## 操作三：Lint（健康审查）

触发：「lint一下」「检查知识库健康状态」「wiki有没有问题？」

### 检查清单

**结构完整性**：
- [ ] 每个章节有章总述文件（`{章号}-{章名}.md`）？
- [ ] 每个节有节总述文件（在节目录内）？
- [ ] **每个小节有小节页文件（在对应小节目录内）**？
- [ ] 环节文件的前驱/后继链接正确？

**文件位置规范**：
- [ ] 小节页文件是否在对应的小节目录内？（不是在外层）
- [ ] 节总述文件是否在对应节目录内？（不是在父目录）

**引用一致性**：
- [ ] 所有 `[[]]` 引用指向存在的文件？（无死链接）
- [ ] 无孤立页面（无入站链接）？
- [ ] 双向引用一致？（A→B 则 B→A）

**Frontmatter 规范**：
- [ ] `chapter` / `abschnitt` / `unterabschnitt` / `Position` 字段正确？
- [ ] `vorheriges` / `nächstes` 链接正确？

**内容质量**：
- [ ] 每个文件有 `## 思辨注释`？
- [ ] 注释包含 an sich / für sich / an und für sich 分析？
- [ ] 注释阐述扬弃关系？

**索引一致性**：
- [ ] `_index/index.md` 与实际页面一致？
- [ ] `_index/log.md` 记录所有 ingest？

### 输出

```
┌─────────────────────┬────────┬──────────────────────────┐
│ 检查项              │ 状态   │ 备注                     │
├─────────────────────┼────────┼──────────────────────────┤
│ 章总述完整性        │ ✓/✗    │                          │
│ 节总述完整性         │ ✓/✗    │                          │
│ 小节页完整性         │ ✓/✗    │ 小节页是否在正确位置？    │
│ 环节链接连续性       │ ✓/✗    │                          │
│ 死链接              │ ✓/✗    │ 找到 N 个                │
│ 孤立页面            │ ✓/✗    │ 找到 N 个                │
│ Frontmatter 规范    │ ✓/✗    │ N 个需修复               │
│ 思辨注释完整性       │ ✓/✗    │ N 个缺少注释             │
│ 索引一致性          │ ✓/✗    │                          │
└─────────────────────┴────────┴──────────────────────────┘
```

发现问题时提出修复建议，修复前与用户确认。

---

## 错误预防

| 错误 | 预防 |
|------|------|
| 目录结构与原书不对应 | 预先分析原书结构，参照 Ingest-Leitfaden 确认边界 |
| 节标题使用简写而非完整标题 | 参照原书目录，使用完整标题如 `A-Der-wahre-Geist-die-Sittlichkeit` |
| 小节页放在错误位置 | **小节页必须在对应小节目录内**，不是在外层 |
| 环节划分过于机械 | 按内容主题划分，与用户确认边界 |
| 忘记思辨注释 | 每个文件创建后即补充 `## 思辨注释` |
| 前后链接断裂 | 创建时同时更新前驱和后继 |
| 索引未更新 | ingest 最后一步固定更新索引 |

---

## 扩展规则

**添加哲学家**：确认该哲学家著作的章/节/小节结构 → 在 `Wiki/` 下建目录 → 按四级结构建立目录 → 在 `Raw/Primärquellen/` 下建目录 → 更新索引

**添加新著作**：在对应哲学家目录下创建新著作目录 → 参照 Ingest-Leitfaden 建立结构 → 创建 `{著作名}-Ingest-Leitfaden.md` → 更新索引

---

*本 Skill 将随知识库的演化而更新。*