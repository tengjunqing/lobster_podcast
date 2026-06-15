#!/usr/bin/env python3
"""
音频后处理脚本 v1.0
功能：降噪 + 响度标准化 + ID3元数据嵌入
用法：python3 audio_postprocess.py <input.mp3> <output.mp3> [--title TITLE] [--artist ARTIST] [--cover PATH]
"""

import subprocess
import sys
import os
import argparse

# ====== 默认配置 ======
DEFAULT_ARTIST = "小王"
DEFAULT_COPYRIGHT = "© 2026 虾聊AI"
DEFAULT_COVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover.png")

# 响度参数（EBU R128 标准）
LOUDNESS_I = -16      # Integrated Loudness (LUFS)
LOUDNESS_LRA = 11     # Loudness Range
LOUDNESS_TP = -1.5    # True Peak

# 降噪参数（afftdn）
DENOISE_NR = 15          # 降噪强度 (0.01-97)，越大越强
DENOISE_NF = -35         # 噪底阈值 dB (-80 到 -20)，越低降噪越激进
# ====================


def postprocess_audio(input_path, output_path, title=None, artist=None, copyright=None, cover_path=None):
    """
    音频后处理流水线：
    1. 降噪（FFT 方法）
    2. 响度标准化（EBU R128）
    3. ID3 元数据嵌入
    """
    artist = artist or DEFAULT_ARTIST
    copyright = copyright or DEFAULT_COPYRIGHT
    cover_path = cover_path or DEFAULT_COVER

    # 检查输入文件
    if not os.path.exists(input_path):
        print(f"❌ 输入文件不存在: {input_path}")
        return False

    # 构建 FFmpeg 滤镜链
    # 步骤1: 降噪 (afftdn)
    # 步骤2: 响度标准化 (loudnorm, 单次处理模式)
    audio_filter = (
        f"afftdn=nr={DENOISE_NR}:nf={DENOISE_NF},"
        f"loudnorm=I={LOUDNESS_I}:LRA={LOUDNESS_LRA}:TP={LOUDNESS_TP}:print_format=summary"
    )

    # 构建 FFmpeg 命令（注意：所有 -i 输入必须在滤镜/输出参数之前）
    cmd = ["ffmpeg", "-y", "-i", input_path]

    # 如果有封面图，作为第二个输入
    has_cover = os.path.exists(cover_path)
    if has_cover:
        cmd.extend(["-i", cover_path])

    # 音频滤镜（必须在所有 -i 之后）
    cmd.extend(["-af", audio_filter])

    # 流映射：音频来自第一个输入，视频（封面）来自第二个输入
    if has_cover:
        cmd.extend(["-map", "0:a", "-map", "1:v"])
        cmd.extend(["-c:v", "mjpeg"])
        cmd.extend(["-disposition:v:0", "attached_pic"])
        cmd.extend(["-metadata:s:v", "mimetype=image/png"])
        cmd.extend(["-metadata:s:v", "comment=Cover (front)"])

    # 音频编码参数
    cmd.extend([
        "-c:a", "libmp3lame",
        "-b:a", "128k",           # 128kbps 恒定码率
        "-ar", "44100",           # 采样率 44.1kHz
        "-ac", "1",               # 单声道（播客标准）
    ])

    # 添加 ID3 元数据
    if title:
        cmd.extend(["-metadata", f"title={title}"])
    cmd.extend(["-metadata", f"artist={artist}"])
    cmd.extend(["-metadata", f"copyright={copyright}"])
    cmd.extend(["-metadata", "album=虾聊AI"])
    cmd.extend(["-metadata", "genre=Technology"])

    # ID3v2.3 标签（兼容性最好）
    cmd.extend(["-id3v2_version", "3"])
    cmd.extend(["-write_id3v1", "1"])  # 同时写 ID3v1 兼容

    cmd.append(output_path)

    print(f"🔧 开始音频后处理...")
    print(f"   输入: {input_path}")
    print(f"   输出: {output_path}")
    print(f"   降噪: afftdn (nr={DENOISE_NR}, nf={DENOISE_NF}dB)")
    print(f"   响度: {LOUDNESS_I} LUFS (LRA={LOUDNESS_LRA}, TP={LOUDNESS_TP})")
    if title:
        print(f"   标题: {title}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            print(f"❌ FFmpeg 处理失败:")
            print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False

        # 输出响度信息
        if "Input Integrated" in result.stderr:
            for line in result.stderr.split("\n"):
                if any(k in line for k in ["Integrated", "LRA", "True Peak"]):
                    print(f"   {line.strip()}")

        output_size = os.path.getsize(output_path) / 1024
        print(f"✅ 后处理完成: {output_path} ({output_size:.1f}KB)")
        return True

    except subprocess.TimeoutExpired:
        print("❌ 处理超时（>120秒）")
        return False
    except Exception as e:
        print(f"❌ 处理异常: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="播客音频后处理")
    parser.add_argument("input", help="输入音频文件路径")
    parser.add_argument("output", help="输出音频文件路径")
    parser.add_argument("--title", help="节目标题（嵌入 ID3）")
    parser.add_argument("--artist", default=DEFAULT_ARTIST, help="主播名")
    parser.add_argument("--copyright", default=DEFAULT_COPYRIGHT, help="版权信息")
    parser.add_argument("--cover", default=DEFAULT_COVER, help="封面图路径")

    args = parser.parse_args()

    success = postprocess_audio(
        input_path=args.input,
        output_path=args.output,
        title=args.title,
        artist=args.artist,
        copyright=args.copyright,
        cover_path=args.cover
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
