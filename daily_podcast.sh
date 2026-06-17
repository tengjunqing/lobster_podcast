#!/bin/bash
# 每日播客自动化脚本 v2.0
# 由 OpenClaw Agent 调用，执行完整的播客生成流程
# 新增：片头拼接 + BGM背景音乐混合
#
# 用法：bash daily_podcast.sh <人声音频路径> <日期标签> [标题] [描述]
# 示例：bash daily_podcast.sh /tmp/podcast_raw.mp3 20260603_Morning "AI双雄冲刺IPO" "本期要点..."

set -e

PODCAST_DIR="$HOME/lobster_podcast"
VOICE_FILE="$1"
DATE_TAG="$2"
EPISODE_TITLE="$3"
EPISODE_DESC="$4"

if [ -z "$VOICE_FILE" ] || [ -z "$DATE_TAG" ]; then
    echo "用法: bash daily_podcast.sh <人声音频路径> <日期标签> [标题] [描述]"
    echo "示例: bash daily_podcast.sh /tmp/podcast_raw.mp3 20260603_Morning \"AI双雄冲刺IPO\" \"本期要点...\""
    exit 1
fi

cd "$PODCAST_DIR"

# 1. 混音处理：片头 + BGM + 人声 → 最终音频
RAW_FILE="audio/${DATE_TAG}_raw.mp3"
TARGET_FILE="audio/${DATE_TAG}_AINews.mp3"
echo "📁 复制人声: $VOICE_FILE → $RAW_FILE"
cp "$VOICE_FILE" "$RAW_FILE"

echo "🎵 混音处理（片头 + BGM）..."
python3 mix_bgm.py "$RAW_FILE" "$TARGET_FILE"
if [ $? -ne 0 ]; then
    echo "❌ 混音失败，回退到纯人声..."
    cp "$RAW_FILE" "$TARGET_FILE"
fi

# 清理临时人声文件
rm -f "$RAW_FILE"

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
