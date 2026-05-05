# 笔记模板与 Frontmatter 规范

## Begriff（概念笔记）模板

```yaml
---
type: Begriff
layer: Begriffe
Philosoph: {所属哲学家}
Ebene: {体系位置，如 Geist-Ethik}
deutsch: {德语原名}
englisch: {英文译名}
erstes_Auftreten: {首次出现的文本位置}
verwandte_Begriffe: [{相关概念列表}]
stützt_auf: [{支撑此概念的运动笔记列表}]
erstellt: {YYYY-MM-DD}
aktualisiert: {YYYY-MM-DD}
---
```

正文结构：
1. 一句话规定（blockquote）
2. Bestimmung / 规定
3. Begriffliche Bewegung / 概念的内在运动
4. Textstellen / 关键文本
5. Verbindungen / 与其他概念的关系
6. Zugehörige Spannungen / 相关张力

## Bewegung（运动笔记）模板

```yaml
---
type: Bewegung
layer: Bewegungen
Philosoph: {所属哲学家}
Ebene: {体系位置}
Bewegungstyp: {运动类型，如 Dialektik / Anabasis / Transzendentalbewegung}
Quelle: {主要文本来源}
verwandte_Begriffe: [{相关概念列表}]
zugehörige_Momente: [{环节笔记列表}]
zugehörige_Spannungen: [{张力列表}]
erstellt: {YYYY-MM-DD}
aktualisiert: {YYYY-MM-DD}
---
```

正文结构：
1. 一句话概述（blockquote）
2. Übersicht / 运动概述（核心逻辑：A → B → C → D）
3. Die Momente / 运动的环节（链接各环节笔记，每环节一句话简述）
4. Dialektische Bedeutung / 辩证法的示范意义
5. Verwandte Bewegungen / 相关运动笔记
6. Textstellen / 核心文本

## Moment（环节笔记）模板

```yaml
---
type: Moment
layer: Momente
Philosoph: {所属哲学家}
Ebene: {体系位置}
zugehörige_Bewegung: {所属运动笔记}
Position: {在运动中的位置，数字}
verwandte_Begriffe: [{相关概念列表}]
vorheriges_Moment: {前一环节，第一个留空}
nächstes_Moment: {后一环节，最后一个留空}
erstellt: {YYYY-MM-DD}
aktualisiert: {YYYY-MM-DD}
---
```

正文结构：
1. 一句话概述（blockquote）
2. Position in der Bewegung / 在运动中的位置
3. Inhalt / 环节内容
4. Textstellen / 相关文本
5. Verbindungen / 与前后环节的关系（← 前驱 / → 后继）

## Spannung（张力笔记）模板

```yaml
---
type: Spannung
layer: Spannungen
Philosoph: {所属哲学家}
Ebene: {体系位置}
verwandte_Begriffe: [{相关概念列表}]
zugehörige_Bewegungen: [{相关运动列表}]
zugehörige_Momente: [{相关环节列表}]
erstellt: {YYYY-MM-DD}
aktualisiert: {YYYY-MM-DD}
---
```

正文结构：
1. 一句话概述（blockquote）
2. Die zwei Pole / 张力的两端
3. Konkrete Erscheinung / 张力的具体表现
4. Versuchte Lösung / 尝试的调和
5. Status / 当前状态

## Anwendung（应用笔记）模板

```yaml
---
type: Anwendung
layer: Anwendungen
Philosoph: {所属哲学家}
Ebene: {体系位置}
verwandte_Begriffe: [{相关概念列表}]
zugehörige_Bewegungen: [{相关运动列表}]
zugehörige_Spannungen: [{相关张力列表}]
erstellt: {YYYY-MM-DD}
aktualisiert: {YYYY-MM-DD}
---
```

正文结构：
1. 一句话概述（blockquote）
2. Anwendungsszenarien / 应用场景（2-3个，每个含黑格尔式分析+具体案例）
3. Methode / 使用方法（分析步骤）
4. Hinweise / 注意事项

## Studie（二手文献研究笔记）

在 `Wiki/Studien/{Autor-Werk}/` 下创建三个文件：

**Lesenotizen.md**：
```yaml
---
type: Studie
Untertyp: Lesenotiz
Autor: {作者}
Werk: {著作名}
erstellt: {YYYY-MM-DD}
aktualisiert: {YYYY-MM-DD}
---
```

**Kernthesen.md**：
```yaml
---
type: Studie
Untertyp: Kernthesen
Autor: {作者}
Werk: {著作名}
erstellt: {YYYY-MM-DD}
aktualisiert: {YYYY-MM-DD}
---
```

**Verbindungen.md**：
```yaml
---
type: Studie
Untertyp: Verbindungen
Autor: {作者}
Werk: {著作名}
erstellt: {YYYY-MM-DD}
aktualisiert: {YYYY-MM-DD}
---
```
