#!/usr/bin/env bash
#
# Phonetik TTS — 文字转语音并发送
# 依赖：
#   - minimax-multimodal (TTS 生成)
#   - ffmpeg (格式转换)
#   - openclaw CLI (消息发送)
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MINIMAX_TTS="${HOME}/.openclaw/skills/minimax-multimodal/scripts/tts/generate_voice.sh"
# 获取当前 agent workspace（来自 PWD 环境变量）
WORKSPACE="${PWD:-${HOME}/.openclaw}"
OUTPUT_DIR="${WORKSPACE}/phonetik-output"

usage() {
  echo "Usage: $0 <send|generate> [options]"
  echo ""
  echo "Commands:"
  echo "  send     — 生成音频并发送到目标渠道"
  echo "  generate — 仅生成音频文件"
  echo ""
  echo "通用选项："
  echo "  --text TEXT       要转换的文字（必需）"
  echo "  --channel CHANNEL 目标渠道：feishu / discord / telegram（默认 feishu）"
  echo "  --target TARGET    发送目标，飞书为 open_id（send 模式必需）"
  echo "  --voice VOICE     声音 ID（默认 female-tianmei-jingpin）"
  echo ""
  echo "MiniMax 专属选项（不影响其他 TTS 实现）："
  echo "  --speed RATE      语速，范围 0.5~2.0（默认 1.0）"
  echo "  --volume LEVEL    音量，范围 0~10（默认 1.0）"
  echo "  --pitch NUMBER    语调，范围 -12~12（默认 0）"
  echo "  --emotion NAME    情绪：happy / sad / angry / fearful /"
  echo "                     disgusted / surprised / calm / fluent / whisper"
  echo "  --sample-rate HZ  采样率：8000/16000/22050/24000/32000/44100（默认 32000）"
  echo ""
  echo "Generate 模式额外选项："
  echo "  -o, --output PATH 输出文件路径（必需）"
  echo ""
  echo "示例："
  echo "  $0 send --text \"你好\" --channel feishu --target ou_xxx"
  echo "  $0 send --text \"等等我想想（emm）...\" --emotion calm"
  echo "  $0 send --text \"首先...<#1#>然后...<#2#>最后\" --speed 0.8"
  echo "  $0 generate --text \"Hello\" -o /tmp/voice.opus"
  exit 1
}

MODE=""
TEXT=""
CHANNEL="feishu"
TARGET=""
VOICE="female-tianmei-jingpin"
SPEED="1.0"
VOLUME="1.0"
PITCH="0"
EMOTION=""
SAMPLE_RATE="32000"
OUTPUT_PATH=""

# 解析参数
if [[ $# -lt 1 ]]; then
  usage
fi

MODE="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --text)       TEXT="$2";       shift 2 ;;
    --channel)    CHANNEL="$2";    shift 2 ;;
    --target)     TARGET="$2";     shift 2 ;;
    --voice)      VOICE="$2";      shift 2 ;;
    --speed)      SPEED="$2";      shift 2 ;;
    --volume)     VOLUME="$2";     shift 2 ;;
    --pitch)      PITCH="$2";      shift 2 ;;
    --emotion)    EMOTION="$2";    shift 2 ;;
    --sample-rate) SAMPLE_RATE="$2"; shift 2 ;;
    -o|--output)  OUTPUT_PATH="$2"; shift 2 ;;
    *)            echo "未知参数: $1" >&2; usage ;;
  esac
done

# 验证参数
if [[ -z "$TEXT" ]]; then
  echo "错误：需要 --text 参数" >&2
  exit 1
fi

if [[ "$MODE" == "send" && -z "$TARGET" ]]; then
  echo "错误：send 模式需要 --target 参数" >&2
  exit 1
fi

if [[ "$MODE" == "generate" && -z "$OUTPUT_PATH" ]]; then
  echo "错误：generate 模式需要 -o/--output 参数" >&2
  exit 1
fi

if [[ "$MODE" != "send" && "$MODE" != "generate" ]]; then
  echo "错误：未知命令 '$MODE'" >&2
  exit 1
fi

# 确保输出目录存在
mkdir -p "$OUTPUT_DIR"

# 临时文件（mp3，统一生成 mp3 后再转换）
TMP_MP3="${OUTPUT_DIR}/phonetik_tmp_$$.mp3"

cleanup() {
  rm -f "$TMP_MP3"
}
trap cleanup EXIT

# 构建 minimax TTS 参数
TTS_ARGS=("-v" "$VOICE" "-o" "$TMP_MP3")
[[ "$SPEED"    != "1.0"  ]] && TTS_ARGS+=("--speed"     "$SPEED")
[[ "$VOLUME"   != "1.0"  ]] && TTS_ARGS+=("--volume"    "$VOLUME")
[[ "$PITCH"    != "0"     ]] && TTS_ARGS+=("--pitch"     "$PITCH")
[[ -n "$EMOTION"          ]] && TTS_ARGS+=("--emotion"   "$EMOTION")
[[ "$SAMPLE_RATE" != "32000" ]] && TTS_ARGS+=("--sample-rate" "$SAMPLE_RATE")

# 生成 TTS
echo "生成语音: $TEXT" >&2
bash "$MINIMAX_TTS" tts "$TEXT" "${TTS_ARGS[@]}" >/dev/null 2>&1

if [[ ! -f "$TMP_MP3" ]]; then
  echo "错误：TTS 生成失败" >&2
  exit 1
fi

# 根据渠道决定最终格式并输出
FINAL_PATH=""

case "$CHANNEL" in
  feishu)
    # 飞书需要 .opus 格式才显示为语音条
    FINAL_PATH="${OUTPUT_PATH:-${OUTPUT_DIR}/phonetik_$(date +%s).opus}"
    ffmpeg -i "$TMP_MP3" -c:a libopus -b:a 32k -y "$FINAL_PATH" 2>/dev/null
    ;;
  telegram|discord)
    FINAL_PATH="${OUTPUT_PATH:-${OUTPUT_DIR}/phonetik_$(date +%s).mp3}"
    cp "$TMP_MP3" "$FINAL_PATH"
    ;;
  *)
    FINAL_PATH="${OUTPUT_PATH:-${OUTPUT_DIR}/phonetik_$(date +%s).opus}"
    ffmpeg -i "$TMP_MP3" -c:a libopus -b:a 32k -y "$FINAL_PATH" 2>/dev/null
    ;;
esac

# generate 模式：输出文件路径后结束
if [[ "$MODE" == "generate" ]]; then
  echo "$FINAL_PATH"
  exit 0
fi

# === SEND 模式：发送音频 ===
case "$CHANNEL" in
  feishu)
    openclaw message send \
      --channel feishu \
      --target "user:$TARGET" \
      --media "$FINAL_PATH" \
      --message "🔊 语音消息"
    ;;
  telegram)
    openclaw message send \
      --channel telegram \
      --target "$TARGET" \
      --media "$FINAL_PATH" \
      --message "🔊 语音消息"
    ;;
  discord)
    openclaw message send \
      --channel discord \
      --target "$TARGET" \
      --media "$FINAL_PATH" \
      --message "🔊 语音消息"
    ;;
esac

echo "已发送至 $CHANNEL" >&2
