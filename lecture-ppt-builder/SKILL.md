---
name: lecture-ppt-builder
description: 政治哲学课程讲义 PPT 的生成与改版工作流（political-philosophy 项目专用）。按「剧场与纸」设计体系——暖象牙纸底、陶瓶红与青铜金点标、满版古典油画引文页——从 manuscripts/ 的手稿 .docx 逐节对应生成课堂投影用精美课件，支持跨平台（Linux LibreOffice+pdftoppm / Windows PowerPoint COM）逐页渲染验证。当需要为新手稿制作一讲 PPT、重做导论、修改已有讲义版式/字号/配图，或任何 agent 接手本项目的讲义制作时使用。
agent_created: true
---

# Lecture PPT Builder（政治哲学讲义 ·「剧场与纸」）

为本项目（political-philosophy）从手稿 .docx 生成课堂投影用 PPT。
成品质量基准：`出讲义/第一讲_希腊悲剧中的政治哲学.pptx`（59 页）、
`出讲义/第一讲B_索福克勒斯_安提戈涅.pptx`（44 页）与 `出讲义/导论_城邦的诞生与政治之问.pptx`（40 页）——新讲义必须维持同等版式与审美水准。

## 硬性原则（违反即返工）

1. 一页一个论点；引文必带行号出处（如「——《安提戈涅》450–470」）。
2. 页眉 kicker 一律带手稿编号（`2.1 · …` / `3.4 · a` / `3.4 小结`），页面顺序与手稿
   标题层级逐节对应；手稿的 a–d 枚举逐条做独立分页，「小结」显式保留，不得合并打散。
3. 正文不得低于 15pt，引文不得低于 20pt（教室投影、后排可读）。
4. 只用考据过的高清图（古典油画/立像/陶瓶/遗址，文件名带出处）；图片一律焦点裁切（cover_pic + FOCUS 表），
   新图必须登记焦点并渲染验证人物面部。
5. 先读 `references/design-system.md` 与 `references/example-pages.md` 获取色板、字号阶梯、真实调用范例与坑清单全文再动手。色板/字体/画布参数不得更改。

## 环境与跨平台支持

- **Python 包管理**：推荐使用 **uv**（`uv run <脚本>`）。脚本均带 PEP 723 依赖声明头，uv 自动创建隔离环境并按需安装依赖，无需预装包，不污染全局环境。
  - 无 uv 时的退路：任何已安装 `python-pptx`, `Pillow`, `python-docx` 的 Python 3.10+ 解释器亦可直接执行。
- **渲染验证引擎（跨平台双引擎）**：
  - **Linux 环境**：自动调用无头 `libreoffice` / `soffice` 转 PDF，再由 `pdftoppm` 渲染为 1920×1080 高清 PNG；
  - **Windows 环境**：自动调用本机 PowerPoint COM 自动化（`pywin32`）导出 PNG；
  - 统一入口：`uv run scripts/render_preview.py <pptx绝对路径> <预览输出目录>`。
- **字体与中西文混排**：系统需具备思源宋体（Noto Serif CJK SC）、思源黑体（Noto Sans CJK SC）、楷体（AR PL UKai CN 或 STKaiti）与西文字体（Liberation Serif 或 Times New Roman）。中西文字体通过 OpenXML 双轨绑定解耦（西文字体赋默认/Latin，中文字体赋 `a:ea`），确保西文与希腊字母按比例排版、不被识别为全角导致溢出。

## 工作流

### 0. 环境自检与模板冒烟（首次或新环境必跑）
```bash
uv run scripts/smoke_test.py --render
```
检查平台依赖（Linux 下检查 libreoffice/pdftoppm，Windows 下检查 win32com）→ PIL 现场生成仿真油画测试图 → 7 种页型各建一页 → 构建 PPTX → 导出 7 张预览 PNG。全部 PASS 才开工；FAIL 哪项修哪项。

### 1. 读手稿、核层级
```bash
uv run scripts/export_manuscript.py manuscripts/<手稿.docx> [输出.txt]
```
按文档流顺序导出段落（带样式名）与表格（Markdown 行），解决表格位置错漏问题。阅读导出文本，逐节列出标题层级树（含 a–d 枚举、小结、设问句、全部引文及其行号）——**先核结构再排页**，不得凭印象重组手稿逻辑。

### 2. 做页映射表
给每一页指定：手稿编号 + 页型（s_cover/s_section/s_quote/s_dark/s_content/s_compare/s_cards）+ 配图。
- 页型按论证功能选择（对照表见 `references/design-system.md` 第 6 节，调用范式见 `references/example-pages.md`）；
- 长引文（≥4 行）独立成 s_quote 引文页；手稿引文的行号全部保留；
- 配图从 hd_images 按主题选，新图先用 view_file / Read 工具目检原图（防文件名名实不符）。

### 3. 复制模板写 build 脚本
复制 `assets/ppt_template.py` 为目标项目根的 `build_<讲名>.py`：
- 修改 OUT / FOOTER / COVER_KICKER；
- 素材分组常量（PHIL/CIV/...）按当前项目的图片目录结构调整；
- IMG 字典注册本讲用图（带框白边照片用 `precrop()` 预裁）；
- 新图在 FOCUS 表补焦点；
- 在「幻灯片内容」区按页映射表逐页编写，页面代码写在 `prs.save` 之前。
写法参考 `references/example-pages.md` 的真实调用示例。

### 4. 构建 PPTX
```bash
uv run build_<讲名>.py
```
确认输出页数与页映射表严格一致。

### 5. 渲染预览
```bash
uv run scripts/render_preview.py <pptx绝对路径> <预览输出目录>
```
（pptx 路径必须使用绝对路径）。

### 6. 逐页目检（不可省略）
用 view_file / Read 读预览 PNG，**全部页面**逐页检查：
- 溢出（文字撞页脚/出卡片/引文撞出处行）、标点孤行、对齐；
- 裁图：人物面部是否保住（FOCUS 不准就微调坐标重建）；
- 希腊语/拉丁语无乱码方框。
**图片缓存提醒**：重建后复查同一页建议复制成新文件名（`cp 幻灯片N.PNG chk_N.png`）再读，避免部分工具读图缓存旧图。

### 7. 修复与迭代
改 build 脚本时编辑工具一次一个调用（避免并发多处替换相互覆盖丢失）；批量改动用 Python 脚本读全文 `replace` 原子写入（每处 `assert count==1`）。改完 Grep 验证 → 重建 → 重渲染 → 再目检，循环至全部页面合格。

### 8. 交付
- 向用户交付 `出讲义/<讲名>.pptx` 产物，并呈现关键/代表性预览页；
- 清理项目根的临时检查图（chk_*.png 等）；
- 新增素材的焦点/预裁参数回写 `assets/ppt_template.py` 的 FOCUS 表与 `design-system.md` 第 7 节，保持 skill 资产与项目同步。

## 修改已有讲义时

直接改对应讲的 build 脚本（不动模板文件），走第 4–8 步。全局调整（如字号阶梯变更）改模板与对应 build 脚本，并在 `design-system.md` 同步记录。

## 文件说明

- `assets/ppt_template.py` — 全部版式代码（色彩/字体/工具函数/七种页型/FOCUS 表），新讲骨架
- `assets/reference_pages/` — 四张成品基准页（封面/深色设问/双栏对照/引文），审美锚点
- `scripts/export_manuscript.py` — 手稿 .docx → 带样式标记的纯文本（段落+表格按文档流），PEP 723
- `scripts/smoke_test.py` — 跨平台环境自检 + 七种页型冒烟构建与渲染验证，PEP 723
- `scripts/render_preview.py` — 跨平台逐页渲染 PNG（1920×1080，Windows COM + Linux LibreOffice 双引擎），PEP 723
- `references/design-system.md` — 设计规范全文：色板、字号阶梯、页型选型表、素材约定、46条焦点档案、工具链坑清单
- `references/example-pages.md` — 七种页型的真实调用示例 + 措辞节奏规范
