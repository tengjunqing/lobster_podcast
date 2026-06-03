#!/bin/bash
# 播客自动部署脚本
# 用法：在 OpenClaw 中由 Agent 自动调用，或手动执行
# 功能：生成 RSS → Git 提交 → Push 到 GitHub Pages

set -e

PODCAST_DIR="$HOME/lobster_podcast"
cd "$PODCAST_DIR"

echo "🎙️ 开始部署播客..."

# 如果有新的脚本文件，用 edge-tts 生成音频
SCRIPT_DIR="$PODCAST_DIR/scripts"
AUDIO_DIR="$PODCAST_DIR/audio"
DATE_TAG=$(date '+%Y%m%d')

# 查找今天最新的脚本
LATEST_SCRIPT=$(ls -t "$SCRIPT_DIR"/${DATE_TAG}*.txt 2>/dev/null | head -1)
if [ -n "$LATEST_SCRIPT" ] && [ ! -f "$AUDIO_DIR/${DATE_TAG}_Morning_AINews.mp3" ]; then
    echo "🎤 用 Edge TTS 生成语音..."
    edge-tts --voice zh-CN-XiaoxiaoNeural --text "$(cat "$LATEST_SCRIPT")" --write-media "$AUDIO_DIR/${DATE_TAG}_Morning_AINews.mp3"
fi

# 1. 生成最新的 feed.xml
echo "📡 生成 RSS Feed..."
python3 generate_feed.py

# 2. Git 提交
echo "📦 Git 提交..."
git add -A
git commit -m "🎙️ 自动更新播客 $(date '+%Y-%m-%d %H:%M')" || echo "没有新的变更需要提交"

# 3. 推送到 GitHub
echo "🚀 推送到 GitHub Pages..."
git push origin main

echo "✅ 部署完成！"
echo "📡 RSS 地址：https://jeffrey628.github.io/lobster_podcast/feed.xml"
