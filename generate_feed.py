#!/usr/bin/env python3
"""
播客 RSS Feed 生成器
扫描 audio/ 目录，自动生成符合 Apple Podcasts 标准的 feed.xml
"""

import os
import glob
import json
from datetime import datetime
import email.utils
import xml.etree.ElementTree as ET

# ====== 配置项 ======
BASE_URL = "https://tengjunqing.github.io/lobster_podcast"
PODCAST_TITLE = "虾聊AI"
PODCAST_DESC = "虾聊AI是一档专注AI与科技领域的每日播客，由AI主播小王为你播报。每天5-8分钟，覆盖：AI大模型最新动态（OpenAI、Anthropic、Google、国产大模型）、科技圈重大事件与产品发布、行业趋势与深度分析、有趣的AI应用和工具推荐。无论你是AI从业者、科技爱好者，还是想跟上时代节奏的普通人，虾聊AI都是你的每日信息伴侣。每天早上7:30更新，通勤路上听一听，轻松跟上AI时代。"
PODCAST_AUTHOR = "小王"
PODCAST_LANGUAGE = "zh-cn"
PODCAST_IMAGE = f"{BASE_URL}/cover.png"
PODCAST_OWNER_NAME = "JeffreyTT"
PODCAST_OWNER_EMAIL = "tengjunqing@163.com"
PODCAST_CATEGORY = "Technology"
# ====================


def get_audio_files():
    """扫描 audio 目录下的 mp3/m4a 文件，按时间从新到旧排序"""
    files = glob.glob("audio/*.mp3") + glob.glob("audio/*.m4a")
    files.sort(key=os.path.getmtime, reverse=True)
    return files


def load_episodes_meta():
    """加载 episodes.json 中的标题和描述"""
    if os.path.exists("episodes.json"):
        with open("episodes.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("episodes", {})
    return {}


def find_episode_meta(date_tag, episodes_meta):
    """根据文件名查找匹配的元数据（支持前缀匹配）"""
    # 直接匹配
    if date_tag in episodes_meta:
        return episodes_meta[date_tag]
    # 前缀匹配（如 20260612_Morning_AINews 匹配 20260612_Morning）
    for key, value in episodes_meta.items():
        if date_tag.startswith(key):
            return value
    return None


def format_duration(seconds):
    """将秒数转换为 HH:MM:SS 格式"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def generate_rss():
    audio_files = get_audio_files()

    rss_items = []
    for file_path in audio_files:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        stat = os.stat(file_path)

        # 发布时间（RFC 822 格式）
        pub_date = email.utils.formatdate(stat.st_mtime, usegmt=True)

        # 从文件名提取日期标签（如 20260612_Morning_AINews）
        date_tag = os.path.splitext(file_name)[0]
        
        # 从 episodes.json 读取标题和描述
        episodes_meta = load_episodes_meta()
        episode_meta = find_episode_meta(date_tag, episodes_meta)
        if episode_meta:
            episode_title = episode_meta.get("title", date_tag.replace("_", " "))
            episode_desc = episode_meta.get("description", f"AI 生成于 {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')}")
        else:
            episode_title = date_tag.replace("_", " ")
            episode_desc = f"AI 生成于 {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')}"

        # 音频直链
        audio_url = f"{BASE_URL}/audio/{file_name}"

        # 判断 MIME 类型
        mime_type = "audio/mpeg" if file_name.endswith(".mp3") else "audio/mp4"

        # 尝试估算时长（基于文件大小粗略估算，MP3 128kbps ≈ 16KB/s）
        est_duration_sec = int(file_size / 16000) if file_name.endswith(".mp3") else int(file_size / 20000)
        duration_str = format_duration(est_duration_sec)

        item_xml = f"""    <item>
      <title>{episode_title}</title>
      <description>{episode_desc}</description>
      <pubDate>{pub_date}</pubDate>
      <enclosure url="{audio_url}" length="{file_size}" type="{mime_type}"/>
      <guid isPermaLink="true">{audio_url}</guid>
      <itunes:duration>{duration_str}</itunes:duration>
      <itunes:author>{PODCAST_AUTHOR}</itunes:author>
      <itunes:episodeType>full</itunes:episodeType>
    </item>"""
        rss_items.append(item_xml)

    # 组装完整 RSS XML
    full_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{PODCAST_TITLE}</title>
    <link>{BASE_URL}</link>
    <language>zh-CN</language>

    <itunes:type>episodic</itunes:type>
    <description>{PODCAST_DESC}</description>
    <itunes:author>{PODCAST_AUTHOR}</itunes:author>
    <itunes:summary>{PODCAST_DESC}</itunes:summary>
    <itunes:explicit>false</itunes:explicit>
    <itunes:category text="{PODCAST_CATEGORY}"/>
    <itunes:owner>
      <itunes:name>{PODCAST_OWNER_NAME}</itunes:name>
      <itunes:email>{PODCAST_OWNER_EMAIL}</itunes:email>
    </itunes:owner>
    <itunes:image href="{PODCAST_IMAGE}"/>
    <atom:link href="{BASE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(rss_items)}
  </channel>
</rss>"""

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(full_xml.strip())

    print(f"✅ RSS Feed 更新成功！共 {len(rss_items)} 集")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    generate_rss()
