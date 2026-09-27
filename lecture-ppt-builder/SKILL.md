---
name: lecture-ppt-builder
description: 政治哲学课程讲义 PPT 的生成与改版工作流（political-philosophy 项目专用）。按「剧场与纸」设计体系——暖象牙纸底、陶瓶红与青铜金点标、满版古典油画引文页——从 manuscripts/ 的手稿 .docx 逐节对应生成课堂投影用精美课件，并用本机 PowerPoint COM 逐页渲染验证。当需要为新手稿制作一讲 PPT、重做导论、修改已有讲义版式/字号/配图，或任何 agent 接手本项目的讲义制作时使用。
agent_created: true
---

# Lecture PPT Builder（政治哲学讲义 ·「剧场与纸」）

为本项目（political-philosophy）从手稿 .docx 生成课堂投影用 PPT。
成品质量基准：`出讲义/第一讲_希腊悲剧中的政治哲学.pptx`（59 页）与
`出讲义/第一讲B_索福克勒斯_安提戈涅.pptx`（44 页）——新讲义必须维持同等版式与审美水准。

## 硬性原则（违反即返工）

1. 一页一个论点；引文必带行号出处（如「——《安提戈涅》450–470」）。
2. 页眉 kicker 一律带手稿编号（`2.1 · …` / `3.4 · a` / `3.4 小结`），页面顺序与手稿
   标题层级逐节对应；手稿的 a–d 枚举逐条做独立分页，「小结」显式保留，不得合并打散。
3. 正文不得低于 15pt，引文不得低于 20pt（教室投影、后排可读）。
4. 只用 `assets/hd_images/` 的考据高清图；图片一律焦点裁切（cover_pic + FOCUS 表），
   新图必须登记焦点并渲染验证人物面部。
5. 先读 `references/design-system.md` 获取色板、字号阶梯、素材档案与坑清单全文，
   再动手。色板/字体/画布参数不得更改。

## 环境与依赖

- Windows bash 工具：每条命令先 `export PATH="/usr/bin:/bin:/usr/local/bin:$PATH"`。
- Python 解释器（含 python-pptx / python-docx / Pillow / pywin32，勿用项目 .venv）：
  `C:\Users\tayhe\.workbuddy\binaries\python\envs\default\Scripts\python.exe`
- 渲染验证依赖本机 PowerPoint（COM 自动化）。

## 工作流

### 1. 读手稿、核层级
用 python-docx 把手稿导出为带样式标记的文本（`[{p.style.name}] {text}`，写 /tmp 后 Read）。
逐节列出标题层级树（含 a–d 枚举、小结、设问句、全部引文及其行号）——
**先核结构再排页**，不得凭印象重组手稿逻辑。

### 2. 做页映射表
给每一页指定：手稿编号 + 页型（s_cover/s_section/s_quote/s_dark/s_content/s_compare/s_cards）
+ 配图。页型按论证功能选择（对照表见 design-system.md 第 6 节）。
长引文（≥4 行）独立成 s_quote 引文页；手稿引文的行号全部保留。
配图从 hd_images 按主题选，新图先 Read 目检原图（文件名可能名实不符）。

### 3. 复制模板写 build 脚本
复制 `assets/ppt_template.py` 为项目根 `build_<讲名>.py`（如 build_第二讲.py）：
- 改 OUT / FOOTER / COVER_KICKER；
- IMG 注册本讲图片（带框白边照片用 precrop 预裁）；
- 新图在 FOCUS 表补焦点；
- 在「幻灯片内容」区按页映射表逐页编写，页面代码写在 `prs.save` 之前。
参考成品脚本：项目根 `build_第一讲.py`、`build_第一讲B.py`。

### 4. 构建
`python build_<讲名>.py`，确认输出页数与页映射表一致。

### 5. 渲染预览
`python <skill目录>/scripts/render_preview.py <pptx绝对路径> <预览输出目录>`
（项目根的 `scripts/render_preview.py` 是同一脚本）。pptx 路径必须绝对路径。

### 6. 逐页目检（不可省略）
用 Read 读预览 PNG，**全部页面**逐页检查：
- 溢出（文字撞页脚/出卡片/引文撞出处行）、标点孤行、对齐；
- 裁图：人物面部是否保住（FOCUS 不准就调坐标重建）；
- 希腊语/拉丁语无乱码方框。
**Read 有图片缓存**：重建后复查同一页必须先复制成新文件名（`cp 幻灯片N.PNG chk_N.png`）再读。

### 7. 修复与迭代
改 build 脚本时 Edit 工具一次一个调用（同消息多 Edit 会互相覆盖丢编辑）；
批量改动用 Python 脚本读全文 replace 原子写入（每处 `assert count==1`）。
改完 Grep 验证 → 重建 → 重渲染 → 再目检。循环至全部页面合格。

### 8. 交付
- present_files 提交 pptx + 代表性预览页；
- 项目根的临时检查图（chk_*.png 等）清理干净；
- 追加当日 `.workbuddy/memory/YYYY-MM-DD.md` 工作日志；
- 新增素材的焦点/预裁参数若未进模板，回写 `assets/ppt_template.py` 的 FOCUS 表
  与 design-system.md 第 7 节，保持 skill 与项目同步。

## 修改已有讲义时

直接改对应 build 脚本（不动模板文件），走第 4–8 步。全局调整（如字号阶梯变更）
改模板与对应 build 脚本，并在 design-system.md 同步记录。

## 文件说明

- `assets/ppt_template.py` — 全部版式代码（色彩/字体/工具函数/七种页型/FOCUS 表），新讲骨架
- `scripts/render_preview.py` — PowerPoint COM 逐页渲染 PNG（1920×1080）
- `references/design-system.md` — 设计规范全文：色板、字号阶梯、页型选型表、
  素材库约定与名实不符警告、46 条焦点档案、工具链坑清单、已完成讲义档案
