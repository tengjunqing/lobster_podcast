#!/bin/bash
# 每日播客自动化脚本
# 由 OpenClaw Agent 调用，执行完整的播客生成流程
#
# 用法：bash daily_podcast.sh <音频文件路径> <日期标签>
# 示例：bash daily_podcast.sh /tmp/podcast_20260603.mp3 20260603_Morning

set -e

PODCAST_DIR="$HOME/lobster_podcast"
AUDIO_FILE="$1"
DATE_TAG="$2"

if [ -z "$AUDIO_FILE" ] || [ -z "$DATE_TAG" ]; then
    echo "用法: bash daily_podcast.sh <音频文件路径> <日期标签>"
    echo "示例: bash daily_podcast.sh /tmp/podcast.mp3 20260603_Morning"
    exit 1
fi

cd "$PODCAST_DIR"

# 1. 复制音频到播客目录
TARGET_FILE="audio/${DATE_TAG}_AINews.mp3"
echo "📁 复制音频: $AUDIO_FILE → $TARGET_FILE"
cp "$AUDIO_FILE" "$TARGET_FILE"

# 2. 生成 RSS Feed
echo "📡 生成 RSS Feed..."
python3 generate_feed.py

# 3. Git 提交和推送
echo "📦 提交并推送..."
git add -A
git commit -m "🎙️ 新增播客: ${DATE_TAG}" || echo "无变更"
git push origin main

echo "✅ 播客发布成功！"
echo "🎧 音频文件: $TARGET_FILE"
echo "📡 RSS: https://jeffrey628.github.io/lobster_podcast/feed.xml"
