#!/bin/bash
# 播客自动部署脚本
# 用法：在 OpenClaw 中由 Agent 自动调用，或手动执行
# 功能：生成 RSS → Git 提交 → Push 到 GitHub Pages

set -e

PODCAST_DIR="$HOME/lobster_podcast"
cd "$PODCAST_DIR"

echo "🎙️ 开始部署播客..."

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
