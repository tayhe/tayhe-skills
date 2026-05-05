# Frontmatter 字段规格

## 通用字段（所有笔记必填）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `type` | string | 笔记类型 | `Begriff` / `Bewegung` / `Moment` / `Spannung` / `Anwendung` / `Studie` |
| `layer` | string | 所属层级（与目录名一致） | `Begriffe` / `Bewegungen` / `Momente` / `Spannungen` / `Anwendungen` |
| `Philosoph` | string | 所属哲学家 | `Hegel` / `Plato` / `Kant` / `Wittgenstein` / `Nietzsche` |
| `Ebene` | string | 在体系中的位置 | `Geist-Ethik` / `Logik-Sein` / `Geist-Selbstbewusstsein` |
| `erstellt` | date | 创建日期 | `2026-05-05` |
| `aktualisiert` | date | 最后更新日期 | `2026-05-05` |

## Begriff（概念笔记）专属字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `deutsch` | string | ✓ | 德语原名 |
| `englisch` | string | | 英文译名 |
| `griechisch` | string | | 希腊语原名（如有） |
| `erstes_Auftreten` | string | ✓ | 首次出现的文本位置 |
| `weitere_Auftreten` | list[string] | | 其他出现位置 |
| `verwandte_Begriffe` | list[string] | ✓ | 相关概念（`[[]]` 格式） |
| `stützt_auf` | list[string] | ✓ | 支撑此概念的运动笔记（`[[]]` 格式） |

## Bewegung（运动笔记）专属字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `Bewegungstyp` | string | ✓ | 运动类型（`Dialektik` / `Anabasis` / `Transzendentalbewegung` / `Sprachspielwechsel` / `Perspektivenwechsel` 等） |
| `Quelle` | string | ✓ | 主要文本来源 |
| `verwandte_Begriffe` | list[string] | ✓ | 相关概念 |
| `zugehörige_Momente` | list[string] | ✓ | 所属环节笔记列表 |
| `zugehörige_Spannungen` | list[string] | | 相关张力列表 |

## Moment（环节笔记）专属字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `zugehörige_Bewegung` | string | ✓ | 所属运动笔记（`[[]]` 格式） |
| `Position` | integer | ✓ | 在运动中的位置（1, 2, 3...） |
| `verwandte_Begriffe` | list[string] | ✓ | 相关概念 |
| `vorheriges_Moment` | string | | 前一环节（第一个环节留空） |
| `nächstes_Moment` | string | | 后一环节（最后一个环节留空） |

## Spannung（张力笔记）专属字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `verwandte_Begriffe` | list[string] | ✓ | 相关概念 |
| `zugehörige_Bewegungen` | list[string] | ✓ | 相关运动 |
| `zugehörige_Momente` | list[string] | | 相关环节 |

## Anwendung（应用笔记）专属字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `verwandte_Begriffe` | list[string] | ✓ | 相关概念 |
| `zugehörige_Bewegungen` | list[string] | ✓ | 相关运动 |
| `zugehörige_Spannungen` | list[string] | | 相关张力 |

## Studie（二手文献研究）专属字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `Untertyp` | string | ✓ | `Lesenotiz` / `Kernthesen` / `Verbindungen` |
| `Autor` | string | ✓ | 作者名 |
| `Werk` | string | ✓ | 著作名 |

## 引用格式规范

- **内部引用**：使用 Obsidian `[[]]` 双向链接格式
- **跨层级引用**：使用相对路径 `[[Begriffe/Sittlichkeit]]`
- **同层引用**：直接使用 `[[Sittlichkeit]]`
- **列表字段**：YAML 列表格式 `["[[概念1]]", "[[概念2]]"]`
