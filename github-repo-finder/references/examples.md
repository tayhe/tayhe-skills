# GitHub Repo Finder - Examples & Templates

## Keyword Generation Examples

### Example 1: "Python Reddit 爬虫，不需要官方API"

**核心通用词（3组）：**
- "reddit scraper"                    ← 技术角度：scraper
- "reddit crawler"                    ← 技术角度：crawler（不同术语）
- "reddit data extraction"            ← 功能角度：数据提取

**特色需求词（3组）：**
- "reddit scraper without api"        ← 爬虫 + 无API
- "reddit unofficial api"             ← Reddit + 非官方API
- "reddit scraping no auth"           ← 抓取 + 无需认证

---

### Example 2: "PDF 发票自动识别提取，要能识别中文"

**核心通用词（3组）：**
- "invoice ocr"                       ← 技术角度：发票OCR
- "pdf document parsing"              ← 技术角度：PDF文档解析
- "receipt recognition"               ← 功能角度：收据识别

**特色需求词（3组）：**
- "invoice ocr chinese"               ← 发票OCR + 中文
- "pdf table extraction asia"         ← PDF表格提取 + 亚洲语言
- "receipt scanner multilingual"      ← 收据扫描 + 多语言

---

### Example 3: "视频自动加字幕 语音转文字"

**核心通用词（3组）：**
- "video subtitle generator"          ← 功能角度：字幕生成
- "speech to text"                    ← 技术角度：语音转文字
- "auto caption"                      ← 产品角度：自动字幕

**特色需求词（3组）：**
- "video subtitle whisper"            ← 字幕 + Whisper模型
- "speech to text offline"            ← 语音转文字 + 离线
- "auto caption local"                ← 自动字幕 + 本地运行

---

### Example 4: "批量把 Word 转成 PDF，要支持命令行"

**核心通用词（3组）：**
- "docx to pdf"                       ← 格式角度：Word转PDF
- "document converter"                ← 功能角度：文档转换
- "word pdf batch"                    ← 场景角度：批量处理

**特色需求词（3组）：**
- "docx pdf cli"                      ← Word转PDF + 命令行
- "document converter python"         ← 文档转换 + Python（用户提到脚本）
- "word to pdf api"                   ← Word转PDF + API接口

---

## Output Card Template

```
排名x：仓库名

仓库: owner/repo
链接: https://github.com/owner/repo
Clone: git clone https://github.com/owner/repo.git
Star: 数量
语言: Python / TypeScript / ...
License: MIT / Apache 2.0 / ...
最后更新: 日期（x天前）
总分: xx / 25

README 摘要：
用 2-3 句话概括这个项目是做什么的、核心功能是什么、怎么用。

仓库特色：
- 特色1：这个仓库与众不同的地方
- 特色2：技术亮点或独特的设计
- 特色3：生态/插件/集成优势

注意事项：
如果有需要注意的点（依赖多、学习曲线陡、文档差等），在这里说明。
```

---

## Score Sheet Template

| Dimension | Score (1-5) | Notes |
|-----------|-------------|-------|
| Stars | X | >5k=5, >2k=4, >1k=3, >500=2, >100=1 |
| Activity | X | <1mo=5, <3mo=4, <6mo=3, <1yr=2, >1yr=1 |
| License | X | MIT/Apache/BSD=5, LGPL=3, GPL=2, none=1 |
| Match | X | Based on README (5=fully meets) |
| Community | X | Forks, issues, archived status |
| **Total** | **XX/25** | |