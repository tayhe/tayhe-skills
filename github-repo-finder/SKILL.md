---
name: github-repo-finder
description: Search for reusable GitHub repositories based on functional requirements. Use when user needs to find open-source libraries, tools, or projects on GitHub that solve a specific problem.
---

# GitHub Repo Finder

Find the best GitHub repositories for a given functional requirement using a structured 6-step workflow.

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

**示例：** See [examples.md](references/examples.md)

### Step 2: 执行搜索

对每组关键词执行以下命令：

```
gh search repos "{关键词}" --sort=stars --limit=5 --json name,fullName,url,description,stargazersCount,updatedAt,language,license
```

如果用户指定了语言，加上 `--language` 参数。

### Step 3: 去重 + 深度评估

对6组关键词的搜索结果合并去重，**按 star 数量降序排列**。

**评估范围与终止条件：**

```
评估顺序（按优先级）：
1. 所有 star ≥ 500 的仓库（高价值，必评估）
2. star 100-499 的前 15 个（潜力项目）
3. star < 100 的前 10 个（最后备选）

终止条件（满足其一即停止）：
- 已找到 5 个明确符合需求的仓库
- 已评估 25 个仓库仍未找到符合需求的
- 已遍历所有去重后的仓库
```

**核心原则：
永远不要只看 description 判断匹配度**：
- ❌ 错误："description 没写XX功能，所以跳过"
- ✅ 正确："虽然 description 没提，但 star 很高，必须读 README 验证是否真的不符合"

**对每个候选仓库执行：**

1. 基础信息：

```
gh api repos/{owner}/{repo} --jq '{stars: .stargazers_count, forks: .forks_count, open_issues: .open_issues_count, updated: .updated_at, created: .created_at, license: .license.spdx_id, archived: .archived, description: .description, topics: .topics, clone_url: .clone_url, homepage: .homepage}'
```

2. **必读 README** 验证需求匹配：

```
gh api repos/{owner}/{repo}/readme --jq '.content' 2>/dev/null | base64 -d 2>/dev/null
```

如果 README 内容过长，只取前 200 行进行分析。

3. 最近提交活跃度：

```
gh api repos/{owner}/{repo}/commits --jq '.[0:5] | .[] | {date: .commit.author.date, message: .commit.message}' 2>/dev/null
```

**评估流程：**
- 按 star 从高到低读取 README
- 记录匹配状态：✅ 符合 / ❌ 不符合 / ❓ 不确定
- 当找到 5 个符合需求的仓库后，立即停止评估
- 若评估 25 个后仍未找到足够符合条件的，停止并报告

### Step 4: 评分

对符合需求的候选仓库，按以下维度打分（每项1-5分）：

1. **Star 数量**：
   - 大于5k = 5分
   - 大于2k = 4分
   - 大于1k = 3分
   - 大于500 = 2分
   - 大于100 = 1分

2. **活跃度**：
   - 1个月内更新 = 5分
   - 3个月内更新 = 4分
   - 6个月内更新 = 3分
   - 1年内更新 = 2分
   - 超1年更新 = 1分

3. **License 友好度**：
   - MIT/Apache/BSD = 5分
   - LGPL = 3分
   - GPL = 2分
   - 无license = 1分

4. **与需求匹配度**（基于 README 内容判断）：
   - 5分：README 明确说明满足核心需求，功能完整
   - 4分：README 说明满足核心需求，功能有局限
   - 3分：需要查看代码才能确认是否满足
   - 2分：README 模糊，不确定是否满足
   - 1分：明确不符合需求

5. **社区健康度**：
   - 综合 forks、open issues 数量、是否 archived 判断 1-5分

### Step 5: 输出结果

按总分排序，对每个推荐仓库输出以下信息卡片：

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

对每个推荐仓库重复以上卡片格式。

### Step 6: 总结建议

在所有仓库卡片之后，给出：

1. **最终推荐**：最推荐哪个仓库，为什么
2. **组合方案**：如果需要多个库搭配使用，给出搭配建议
3. **快速开始**：推荐仓库的一键 clone 加安装命令
4. **避坑提醒**：某些仓库看着不错但有坑的，提醒一下

## 注意事项

- 关键词一定要用英文搜索
- 如果某个命令执行失败，跳过继续
- 优先推荐最近 6 个月有更新的仓库
- 如果用户没指定语言，默认不限制语言
- 如果结果太少，尝试更宽泛的关键词再搜一轮
- README 摘要要用中文输出，简洁明了
- Clone URL 确保是可直接使用的完整命令
- 仓库特色要结合 README 内容分析，不要泛泛而谈