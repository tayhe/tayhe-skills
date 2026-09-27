# tayhe-skills

为 AI Agents 编写的技能集合。提供面向金融投研、课件生成、知识库维护、文档解析、语音处理、浏览器控制及开源探索等场景的专业技能工具。

---

## Skills 清单

| 分类 | Skill | 说明 |
| :--- | :--- | :--- |
| **内容与知识管理** | [lecture-ppt-builder](./lecture-ppt-builder/) | 政治哲学课程讲义 PPT 生成与改版工作流（「剧场与纸」设计体系，DOCX 转 PPTX，版式与字号校验） |
| | [philosophie-wiki](./philosophie-wiki/) | 哲学知识库维护规范（Karpathy LLM Wiki 模式，文献摄入 Ingest、查询 Query 与 Lint 审查） |
| **金融与投研决策** | [tradingagents](./tradingagents/) | TradingAgents 多智能体金融投研系统（四分析师牛熊攻防辩论 + 交易与风控评级） |
| **文档与多模态** | [paddleocr-parser](./paddleocr-parser/) | 基于 PaddleOCR API 的高精度文档解析（同步/异步任务、表格提取、LaTeX 公式与排版还原） |
| | [phonetik](./phonetik/) | 统一语音总入口：ASR 语音转文字（qwen-voice）+ TTS 语音合成（minimax-multimodal） |
| **开发与探索** | [github-repo-finder](./github-repo-finder/) | 开源仓库检索助手（6步关键词分层拆解、去重评估与结构化评分卡片） |
| **浏览器与调试** | [browser-cdp](./browser-cdp/) | 原生 Python websockets 直连 Chrome CDP 协议自动化（轻量免依赖，截图/JS执行/控制台监听） |
| | [browser-cdp-openclaw](./browser-cdp-openclaw/) | OpenClaw 浏览器 CDP 自动化实践指南（Snapshot-Act 循环、Ref 管理、错误恢复） |
| | [chrome-devtools-mcp](./chrome-devtools-mcp/) | Chrome DevTools MCP 服务协议集成指南（全功能调试、网络追踪、性能分析） |

---

## 目录结构规范

每个 Skill 目录遵循统一的标准结构：

```text
<skill-name>/
├── SKILL.md             # 核心定义文件（包含 YAML frontmatter、触发条件与工作流指南）
├── scripts/             # 可执行脚本与辅助工具（Python 脚本使用 uv 运行与管理环境）
├── references/          # 参考规范、配置模板或设计系统文档（可选）
└── assets/              # 静态资源、演示模板或素材（可选）
```

## 开发与新增 Skill

1. 在项目根目录下创建新的 Skill 目录：`mkdir <skill-name>`
2. 编写 `SKILL.md`（包含 `name`、`description` 等 frontmatter 元数据与执行步骤）
3. 按需在 `scripts/` 添加工具脚本，在 `references/` 添加详细参考手册
4. 更新根目录 `README.md` 中的清单
5. 提交更改：
   ```bash
   git add <skill-name>/ README.md
   git commit -m "feat(<skill-name>): 新增 <skill-name> skill"
   git push
   ```

