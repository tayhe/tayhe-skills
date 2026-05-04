---
name: github-repo-finder
description: >
  专业的开源仓库搜索助手，帮助开发者快速找到可复用的 GitHub 仓库。
  触发条件：(1) 用户描述需要某种功能或工具，想找开源实现
  (2) 用户明确要求搜索 GitHub 仓库
  (3) 用户说"找一个库"、"有没有现成的"、"推荐一个开源项目"等类似意图
  支持任意语言、任意领域的仓库搜索，输出结构化评分卡片。
---

# GitHub Repo Finder

6 步工作流：关键词生成 → 搜索 → 去重评估 → 评分 → 输出 → 建议。

## Workflow

### Step 1: 分析需求，生成搜索关键词

根据用户描述的功能需求，严格拆解为 **6 组英文搜索关键词**：
- **3 组核心通用词**：只包含功能本质，不带任何筛选条件
- **3 组特色需求词**：核心功能 + 本次特殊需求（无API、本地部署、免费、开源等）

**分层生成原则：**

| 层级 | 数量 | 用途 | 关键词特点 |
|------|------|------|-----------|
| **核心通用词** | 3组 | 捕获功能本质，扩大覆盖面 | 只描述"做什么"，**绝不带限定条件**（如without/free/selfhosted等）|
| **特色需求词** | 3组 | 精确匹配特殊约束 | 核心功能 + 用户的特殊需求（无API、离线、本地、免费等）|

**核心原则：**
- 用该领域的专业英文术语
- 每组关键词从不同角度切入（技术类型/功能描述/数据格式）
- **核心通用词绝不带限定条件**，确保能捕获到描述中未写但实际符合的仓库
- 特色需求词必须同时包含：核心功能术语 + 特殊约束

**示例：** 详见 [references/examples.md](references/examples.md) 中的 4 个完整示例。

### Step 2: 执行搜索

对每组关键词执行：

```bash
gh search repos "{关键词}" --sort=stars --limit=5 --json name,fullName,url,description,stargazersCount,updatedAt,language,license
```

用户指定语言时加 `--language` 参数。

也可使用辅助脚本 `scripts/search_repos.py` 批量搜索，支持多关键词一次性执行并自动去重排序：

```bash
python3 scripts/search_repos.py "keyword1" "keyword2" "keyword3"
python3 scripts/search_repos.py --language python "keyword1" "keyword2"
```

### Step 3: 去重 + 深度评估

6 组结果合并去重，按 star 降序排列。

**评估顺序（按优先级）：**
1. 所有 star ≥ 500 的仓库（高价值，必评估）
2. star 100-499 的前 15 个（潜力项目）
3. star < 100 的前 10 个（最后备选）

**终止条件（满足其一即停止）：**
- 已找到 5 个明确符合需求的仓库
- 已评估 25 个仓库仍未找到符合需求的
- 已遍历所有去重后的仓库

**核心原则：永远不只看 description 判断匹配度。** star 高但 description 模糊的仓库，必须读 README 验证。

对每个候选仓库：

```bash
# 基础信息
gh api repos/{owner}/{repo} --jq '{stars: .stargazers_count, forks: .forks_count, open_issues: .open_issues_count, updated: .updated_at, created: .created_at, license: .license.spdx_id, archived: .archived, description: .description, topics: .topics, clone_url: .clone_url, homepage: .homepage}'

# README（超长取前 200 行）
gh api repos/{owner}/{repo}/readme --jq '.content' 2>/dev/null | base64 -d 2>/dev/null

# 最近 5 次提交
gh api repos/{owner}/{repo}/commits --jq '.[0:5] | .[] | {date: .commit.author.date, message: .commit.message}' 2>/dev/null
```

记录匹配状态：✅ 符合 / ❌ 不符合 / ❓ 不确定。

## Step 4: 评分（满分 25）

| 维度 | 5分 | 3分 | 1分 |
|------|-----|-----|-----|
| Star | >5k | >1k | >100 |
| 活跃度 | 1月内更新 | 6月内 | 超1年 |
| License | MIT/Apache/BSD | LGPL | 无license |
| 需求匹配 | README 明确满足核心需求 | 需查代码确认 | 明确不符 |
| 社区健康 | forks 多、issues 活跃、未 archived | 一般 | 差 |

## Step 5: 输出结果

按总分排序，每个推荐仓库输出：

```
排名x：仓库名

仓库: owner/repo
链接: https://github.com/owner/repo
Clone: git clone https://github.com/owner/repo.git
Star / 语言 / License / 最后更新
总分: xx / 25

README 摘要：2-3 句话概括功能与用法（中文）

仓库特色：
- 特色1
- 特色2
- 特色3

注意事项：依赖、学习曲线、文档质量等
```

## Step 6: 总结建议

1. **最终推荐**：最推荐哪个，为什么
2. **组合方案**：多库搭配建议
3. **快速开始**：一键 clone + 安装命令
4. **避坑提醒**：看着好但有坑的仓库

## 注意事项

- 关键词必须用英文
- 命令执行失败则跳过继续
- 优先推荐 6 个月内有更新的仓库
- 用户未指定语言则不限制
- 结果太少时用更宽泛的关键词再搜一轮
- README 摘要用中文，简洁明了
- Clone URL 确保可直接使用