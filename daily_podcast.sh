#!/bin/bash
# 每日播客自动化脚本
# 由 OpenClaw Agent 调用，执行完整的播客生成流程
#
# 用法：bash daily_podcast.sh <音频文件路径> <日期标签> [标题] [描述]
# 示例：bash daily_podcast.sh /tmp/podcast_20260603.mp3 20260603_Morning "AI双雄冲刺IPO" "本期要点：OpenAI与Anthropic同步冲刺IPO..."

set -e

PODCAST_DIR="$HOME/lobster_podcast"
AUDIO_FILE="$1"
DATE_TAG="$2"
EPISODE_TITLE="$3"
EPISODE_DESC="$4"

if [ -z "$AUDIO_FILE" ] || [ -z "$DATE_TAG" ]; then
    echo "用法: bash daily_podcast.sh <音频文件路径> <日期标签> [标题] [描述]"
    echo "示例: bash daily_podcast.sh /tmp/podcast.mp3 20260603_Morning \"AI双雄冲刺IPO\" \"本期要点...\""
    exit 1
fi

cd "$PODCAST_DIR"

# 1. 复制音频到播客目录
TARGET_FILE="audio/${DATE_TAG}_AINews.mp3"
echo "📁 复制音频: $AUDIO_FILE → $TARGET_FILE"
cp "$AUDIO_FILE" "$TARGET_FILE"

# 2. 如果有标题和描述，更新 episodes.json
if [ -n "$EPISODE_TITLE" ]; then
    echo "📝 更新节目信息..."
    python3 -c "
import json
import os

episodes_file = 'episodes.json'
if os.path.exists(episodes_file):
    with open(episodes_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {'episodes': {}}

data['episodes']['$DATE_TAG'] = {
    'title': '''$EPISODE_TITLE''',
    'description': '''$EPISODE_DESC'''
}

with open(episodes_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('✅ 节目信息已更新')
"
fi

# 3. 生成 RSS Feed
echo "📡 生成 RSS Feed..."
python3 generate_feed.py

# 4. Git 提交和推送
echo "📦 提交并推送..."
git add -A
git commit -m "🎙️ 新增播客: ${DATE_TAG}" || echo "无变更"
git push origin main

echo "✅ 播客发布成功！"
echo "🎧 音频文件: $TARGET_FILE"
echo "📡 RSS: https://tengjunqing.github.io/lobster_podcast/feed.xml"
