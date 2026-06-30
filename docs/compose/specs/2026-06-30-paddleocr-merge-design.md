# PaddleOCR Skills 合并设计文档

## [S1] 问题

当前存在 3 个功能高度重叠的 PaddleOCR skill：

- `paddleocr-async`: 异步 API，处理大文档（100+页），每页输出 Markdown，支持断点续传
- `paddleocr-doc-parsing`: 同步 API，支持 PDF 分割、图片优化、表格/公式精确提取
- `paddleocr-doc-parsing-v2`: 双模式（同步+异步），bash 轻量版

核心问题：
1. 环境变量命名不统一（3 套不同的变量名）
2. 依赖栈不一致（httpx vs requests vs curl）
3. 输出格式不统一（每页文件 vs JSON 文件 vs stdout）
4. 功能子集分散（断点续传在 async，PDF 分割在 doc-parsing）

## [S2] 合并目标

统一为单一 skill `paddleocr-parser`，保留所有独特功能，统一接口。

## [S3] 架构设计

```
paddleocr-parser/
├── SKILL.md                    # 统一文档
├── _meta.json                  # 元数据
├── references/
│   └── output_schema.md        # 输出格式说明
└── scripts/
    ├── paddleocr_parse.py      # 统一 CLI 入口
    ├── lib_sync.py             # 同步 API 库
    ├── lib_async.py            # 异步 API 库
    ├── split_pdf.py            # PDF 分割工具
    ├── optimize_file.py        # 图片优化工具
    └── smoke_test.py           # 验证脚本
```

### 环境变量

```bash
# 必填
PADDLEOCR_ACCESS_TOKEN          # API 认证 token

# 可选（有默认值）
PADDLEOCR_SYNC_API_URL          # 同步端点（默认从 PaddleOCR 官网获取）
PADDLEOCR_ASYNC_API_URL         # 异步端点（默认 https://paddleocr.aistudio-app.com/api/v2/ocr/jobs）
```

向后兼容：同时支持旧变量名映射：
- `PADDLEOCR_DOC_PARSING_API_URL` → `PADDLEOCR_SYNC_API_URL`
- `PADDLEOCR_ASYNC_TOKEN` → `PADDLEOCR_ACCESS_TOKEN`
- `PADDLEOCR_API_URL` → `PADDLEOCR_SYNC_API_URL`

### CLI 接口

```bash
uv run scripts/paddleocr_parse.py [OPTIONS] --file-url URL | --file-path PATH

# 模式选择
--mode auto|sync|async          # 默认 auto

# 输出格式
--stdout                        # JSON 输出到 stdout
--output FILE                   # JSON 保存到文件
--output-per-page DIR           # 每页一个 Markdown 文件

# 附加功能
--split-pages "1-5,8"           # PDF 页码范围（仅 sync 模式）
--optimize                      # 自动压缩大图片
--skip-existing                 # 断点续传（仅 async 模式）

# API 参数
--model MODEL                   # 模型名（默认 PaddleOCR-VL-1.5）
--no-deskew                     # 禁用文档矫正
--no-orientation                # 禁用方向识别
--charts                        # 启用图表解析
```

### 自动模式选择逻辑

```
--mode sync  → 强制同步
--mode async → 强制异步
--mode auto  →
    ├─ 图片文件 → sync
    ├─ PDF 且已知 ≤100 页 → sync
    └─ 其他 → async
```

## [S4] API 差异处理

### 同步 API

- 端点：`POST /layout-parsing`
- 认证：`Authorization: token {TOKEN}`
- 请求：JSON body `{file, fileType, useDocOrientationClassify, ...}`
- 响应：`{errorCode: 0, result: {layoutParsingResults: [...]}}`

### 异步 API

- 提交：`POST /api/v2/ocr/jobs`
- 轮询：`GET /api/v2/ocr/jobs/{jobId}`
- 结果：JSONL 下载
- 认证：`Authorization: bearer {TOKEN}`
- 请求：JSON body `{fileUrl/file, model, optionalPayload}`

### 统一处理

`lib_sync.py` 和 `lib_async.py` 分别封装各自 API，对外暴露统一的 `parse_document()` 接口。

## [S5] 输出格式

### 统一 JSON envelope

```json
{
  "ok": true,
  "text": "所有页面拼接的全文",
  "result": {
    "mode": "sync|async",
    "pages": 10,
    "layoutParsingResults": [
      {
        "markdown": {"text": "...", "images": {}},
        "prunedResult": [...],
        "outputImages": {}
      }
    ]
  },
  "error": null
}
```

### 每页文件输出 (--output-per-page)

```
output/
├── doc_0/
│   ├── doc_0.md
│   └── imgs/...
├── doc_1/
│   ├── doc_1.md
│   └── imgs/...
└── ...
```

## [S6] 复用策略

| 来源 | 复用内容 | 修改点 |
|------|---------|--------|
| paddleocr-async | `lib_async.py` 全部逻辑 | 统一环境变量名 |
| paddleocr-doc-parsing | `lib.py` 同步逻辑、`split_pdf.py`、`optimize_file.py` | 统一环境变量名 |
| paddleocr-doc-parsing-v2 | bash 逻辑参考 | 不保留 bash 版本 |

## [S7] 验证标准

1. `smoke_test.py` 通过（配置检查 + API 连通性）
2. 同步模式解析图片文件成功
3. 同步模式解析 PDF 成功
4. 异步模式解析大 PDF 成功
5. `--output-per-page` 输出正确
6. `--skip-existing` 断点续传正常
7. `--split-pages` 页码提取正常
8. `--optimize` 图片压缩正常
