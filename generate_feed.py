#!/usr/bin/env python3
"""
播客 RSS Feed 生成器
扫描 audio/ 目录，自动生成符合 Apple Podcasts 标准的 feed.xml
"""

import os
import glob
from datetime import datetime
import email.utils
import xml.etree.ElementTree as ET

# ====== 配置项 ======
BASE_URL = "https://jeffrey628.github.io/lobster_podcast"  # 替换为你的 GitHub Pages 域名
PODCAST_TITLE = "龙虾 AI 生产力播客"
PODCAST_DESC = "由 AI 自动生成的个人定制语音播客，每日 AI 资讯速递"
PODCAST_AUTHOR = "AI Assistant"
PODCAST_LANGUAGE = "zh-cn"
PODCAST_IMAGE = f"{BASE_URL}/cover.png"  # 可选：播客封面图
# ====================


def get_audio_files():
    """扫描 audio 目录下的 mp3/m4a 文件，按时间从新到旧排序"""
    files = glob.glob("audio/*.mp3") + glob.glob("audio/*.m4a")
    files.sort(key=os.path.getmtime, reverse=True)
    return files


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

        # 从文件名提取标题
        episode_title = os.path.splitext(file_name)[0]
        # 美化标题：替换下划线为空格
        episode_title = episode_title.replace("_", " ")

        # 音频直链
        audio_url = f"{BASE_URL}/audio/{file_name}"

        # 判断 MIME 类型
        mime_type = "audio/mpeg" if file_name.endswith(".mp3") else "audio/mp4"

        # 尝试估算时长（基于文件大小粗略估算，MP3 128kbps ≈ 16KB/s）
        est_duration_sec = int(file_size / 16000) if file_name.endswith(".mp3") else int(file_size / 20000)
        duration_str = format_duration(est_duration_sec)

        item_xml = f"""    <item>
      <title>{episode_title}</title>
      <description>AI 生成于 {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')}</description>
      <pubDate>{pub_date}</pubDate>
      <enclosure url="{audio_url}" length="{file_size}" type="{mime_type}"/>
      <guid isPermaLink="true">{audio_url}</guid>
      <itunes:duration>{duration_str}</itunes:duration>
      <itunes:author>{PODCAST_AUTHOR}</itunes:author>
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
    <language>{PODCAST_LANGUAGE}</language>
    <description>{PODCAST_DESC}</description>
    <itunes:author>{PODCAST_AUTHOR}</itunes:author>
    <itunes:summary>{PODCAST_DESC}</itunes:summary>
    <itunes:explicit>no</itunes:explicit>
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
