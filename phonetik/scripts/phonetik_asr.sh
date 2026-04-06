#!/usr/bin/env bash
#
# Phonetik ASR — 语音转文字
# 依赖：qwen-voice 的 qwen_asr.py
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QWEN_ASR="${HOME}/.openclaw/skills/qwen-voice/scripts/qwen_asr.py"

usage() {
  echo "Usage: $0 <audio_file>"
  echo "  将音频文件转换为文字"
  echo "  支持格式：.ogg .wav .mp3 .opus .m4a"
  echo ""
  echo "示例："
  echo "  $0 ~/.openclaw/media/inbound/voice.ogg"
  exit 1
}

if [[ $# -lt 1 ]]; then
  usage
fi

AUDIO_FILE="$1"

if [[ ! -f "$AUDIO_FILE" ]]; then
  echo "错误：文件不存在: $AUDIO_FILE" >&2
  exit 1
fi

# 检查依赖
if [[ ! -f "$QWEN_ASR" ]]; then
  echo "错误：qwen_asr.py 未找到，请确保 qwen-voice skill 已安装" >&2
  exit 1
fi

# 执行 ASR
python3 "$QWEN_ASR" --in "$AUDIO_FILE"
