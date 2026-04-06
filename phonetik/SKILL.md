---
name: phonetik
description: 语音信息总入口 Skill — 统一管理 ASR（语音转文字）和 TTS（文字转语音）功能。ASR 调用 qwen-voice（qwen3-asr-flash），TTS 调用 minimax-multimodal（TTS）并根据目标渠道自动转换格式，在各平台呈现为语音消息。
---

# Phonetik — 语音总入口

统一语音入口，封装 ASR 和 TTS 两大功能，对上层（LLM/Agent）屏蔽底层实现细节。

> **设计原则**：通用接口（voice_id、text、channel 等）公开给所有 TTS 实现，MiniMax 专属参数（如语速、情绪等）通过文本内嵌标记传递，不写入通用接口规范。

## 前提条件

- `DASHSCOPE_API_KEY` 已配置（qwen-voice ASR 用）
- `MINIMAX_API_KEY` 已配置（minimax-multimodal TTS 用）
- `ffmpeg` 已安装（格式转换用）

---

## ASR — 语音转文字

将用户发送的语音消息转换为文字，供 LLM 处理。

```bash
bash scripts/phonetik_asr.sh <音频文件路径>
```

**支持格式**：`.ogg`、`.wav`、`.mp3`、`.opus`、`.m4a`

**输出**：纯文本（stdout）

**示例**：
```bash
text=$(bash scripts/phonetik_asr.sh ~/.openclaw/media/inbound/voice.ogg)
echo "$text"
```

---

## TTS — 文字转语音

将 LLM 生成的文字回复转换为语音，并根据目标渠道自动选择合适格式。

### 基本用法

```bash
# 生成音频文件（推荐方式，由 agent 的 message 工具发送）
bash scripts/phonetik_tts.sh generate --text "你好" -o minimax-output/voice.opus

# send 模式：生成并发送（受限于 Feishu open_id cross-app 权限）
bash scripts/phonetik_tts.sh send --text "你好" --channel feishu --target ou_xxx
```

### 通用参数

| 参数 | 说明 |
|------|------|
| `send` / `generate` | send=生成+CLI发送，generate=仅生成文件 |
| `--text TEXT` | 要转换的文字 |
| `--channel CHANNEL` | 目标渠道：feishu / discord / telegram（默认 feishu） |
| `--target TARGET` | 发送目标 open_id（send 模式必需） |
| `--voice VOICE` | 声音 ID（默认 female-tianmei-jingpin） |

### 渠道格式说明

| 渠道 | 格式 | 效果 |
|------|------|------|
| `feishu` | .opus | ✅ 显示为语音条 |
| `discord` | .mp3 | ✅ 显示为语音消息 |
| `telegram` | .mp3 | ✅ 显示为语音消息 |

### ⚠️ send 模式的限制

`send` 模式依赖 `openclaw message send` CLI 命令，存在 **open_id cross-app** 权限限制。

**推荐工作流**：使用 `generate` 模式生成音频文件，由 agent 的 `message` 工具发送。

---

## MiniMax 专属参数

> 以下参数仅对 minimax-multimodal 有效，使用其他 TTS 实现时被忽略或无效。

### 语音调控参数

| 参数 | 说明 | 范围 |
|------|------|------|
| `--speed RATE` | 语速，越大越快 | 0.5 ~ 2.0（默认 1.0） |
| `--volume LEVEL` | 音量 | 0 ~ 10（默认 1.0） |
| `--pitch NUMBER` | 语调 | -12 ~ 12（默认 0） |
| `--emotion NAME` | 情绪 | happy / sad / angry / fearful / disgusted / surprised / calm / fluent / whisper |
| `--sample-rate HZ` | 采样率 | 8000 / 16000 / 22050 / 24000 / 32000 / 44100（默认 32000） |

> `--emotion` 中的 `fluent` 和 `whisper` 仅对 speech-2.6 系列模型生效；speech-2.8 系列不支持 whisper。

### 文本内嵌控制（直接在文字中使用）

这些标记直接写在 `--text` 里，无需额外参数：

**停顿控制：**
```
我在想...<#1#>等等...<#2#>好了！
```
`<#x#>` 表示停顿 x 秒（范围 0.01~99.99 秒），最多两位小数。不可连续使用多个停顿标记。

**语气词标签（仅 speech-2.8 系列）：**

| 标签 | 效果 |
|------|------|
| `(laughs)` | 笑声 |
| `(chuckle)` | 轻笑 |
| `(coughs)` | 咳嗽 |
| `(clear-throat)` | 清嗓子 |
| `(groans)` | 呻吟 |
| `(breath)` | 正常换气 |
| `(pant)` | 喘气 |
| `(inhale)` | 吸气 |
| `(exhale)` | 呼气 |
| `(gasps)` | 倒吸气 |
| `(sniffs)` | 吸鼻子 |
| `(sighs)` | 叹气 |
| `(snorts)` | 喷鼻息 |
| `(burps)` | 打嗝 |
| `(lip-smacking)` | 咂嘴 |
| `(humming)` | 哼唱 |
| `(hissing)` | 嘶嘶声 |
| `(emm)` | 嗯 |
| `(sneezes)` | 喷嚏 |

示例：
```
你好呀(laughs)，好久不见！...<#1#>...你最近怎么样？
```

### MiniMax 参数使用示例

```bash
# 慢速、平静情绪
bash scripts/phonetik_tts.sh send \
  --text "嗯...让我想想..." \
  --emotion calm --speed 0.8 \
  --channel feishu --target ou_xxx

# 带有语气词和停顿（播报风格）
bash scripts/phonetik_tts.sh send \
  --text "各位观众大家好(clear-throat)，欢迎收看今天的节目。" \
  --speed 1.0 --pitch 2 \
  --channel feishu --target ou_xxx

# 大音量、高语调（兴奋情绪）
bash scripts/phonetik_tts.sh send \
  --text "太棒了！终于成功了！" \
  --emotion happy --pitch 5 --volume 2.0 \
  --channel feishu --target ou_xxx
```

---

## 内部实现

- **ASR**：调用 `qwen-voice` 的 `qwen_asr.py`
- **TTS**：调用 `minimax-multimodal` 的 `generate_voice.sh`，FFmpeg 转换格式
- **渠道适配**：自动选择 .opus（飞书）或 .mp3（其他平台）

## 工作流示例

### 处理用户语音消息（ASR）

```
用户发送语音 → OpenClaw 接收为 .ogg 文件
→ Phonetik ASR 转换文字
→ LLM 处理文字并生成回复
```

### 发送语音回复（TTS）

```bash
# 推荐方式（generate + message tool）
VOICE_FILE=$(bash scripts/phonetik_tts.sh generate \
  --text "我觉得这个想法很棒！" \
  -o minimax-output/reply.opus)
# → 输出文件路径，由 agent 通过 message 工具发送
```

---

## 文件结构

```
phonetik/
├── SKILL.md
└── scripts/
    ├── phonetik_asr.sh   # ASR 入口
    └── phonetik_tts.sh   # TTS 入口
```
