#!/usr/bin/env python3
"""
播客混音脚本 v4.0
功能：仅片头音乐与人声重叠（看点预告），正文纯人声
用法：python3 mix_bgm.py <人声mp3> <输出mp3> [--intro 片头路径]

混音逻辑（v4.0 - 简化模式）：
- 片头段（前22s）：片头音乐80% + 人声120%（看点预告重叠）
- 正文段：纯人声120%（无BGM）
"""

import subprocess
import sys
import os
import argparse

# 默认路径
PODCAST_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INTRO = os.path.join(PODCAST_DIR, "assets", "intro_30s.mp3")

# 音量参数
INTRO_VOL = 0.80       # 片头音乐音量（80%）
VOICE_VOL = 1.20       # 人声音量（120%）
INTRO_OVERLAP = 22     # 片头与人声重叠时长（秒），覆盖看点预告到"大家好"前


def get_duration(filepath):
    """获取音频时长（秒）"""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        filepath
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def mix_podcast(voice_path, output_path, intro_path=None):
    """
    混音流程（v4.0 简化模式）：
    1. 片头音乐与人声重叠（精彩看点预告效果）
    2. 片头结束后纯人声
    """
    intro_path = intro_path or DEFAULT_INTRO

    # 检查文件
    for f, name in [(voice_path, "人声"), (intro_path, "片头")]:
        if not os.path.exists(f):
            print(f"❌ {name}文件不存在: {f}")
            return False

    # 获取时长
    intro_dur = get_duration(intro_path)
    voice_dur = get_duration(voice_path)
    overlap = min(INTRO_OVERLAP, intro_dur)

    print(f"🎵 混音参数（v4.0 简化模式）:")
    print(f"   片头音乐: {overlap:.0f}s（与人声重叠，看点预告）")
    print(f"   人声: {voice_dur:.1f}s")
    print(f"   总时长: {voice_dur:.1f}s")
    print(f"   🎤 片头段: 音乐{INTRO_VOL*100:.0f}% + 人声{VOICE_VOL*100:.0f}%")
    print(f"   🎤 正文段: 纯人声{VOICE_VOL*100:.0f}%")

    # 构建滤镜 - v4.0 简化混音（仅片头）
    # [0:a]=片头音乐 [1:a]=人声
    filter_complex = (
        # 片头音乐：前 overlap 秒与人声重叠（看点预告），末尾淡出1.5s
        f"[0:a]atrim=duration={overlap},volume={INTRO_VOL},"
        f"afade=t=out:st={overlap-1.5}:d=1.5[intro_vol];"
        # 人声音量增强
        f"[1:a]volume={VOICE_VOL}[voice_vol];"
        # 混合2层
        f"[intro_vol][voice_vol]amix=inputs=2:duration=longest:dropout_transition=0[out]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", intro_path,
        "-i", voice_path,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-c:a", "libmp3lame",
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "1",
        output_path
    ]

    print(f"🔧 开始混音...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"❌ FFmpeg 混音失败:")
            print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False

        output_size = os.path.getsize(output_path) / 1024
        output_dur = get_duration(output_path)
        print(f"✅ 混音完成: {output_path}")
        print(f"   大小: {output_size:.1f}KB")
        print(f"   时长: {output_dur:.1f}s")
        return True

    except subprocess.TimeoutExpired:
        print("❌ 混音超时（>300秒）")
        return False
    except Exception as e:
        print(f"❌ 混音异常: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="播客混音 v4.0（仅片头混音）")
    parser.add_argument("voice", help="人声音频路径")
    parser.add_argument("output", help="输出音频路径")
    parser.add_argument("--intro", default=DEFAULT_INTRO, help="片头路径")

    args = parser.parse_args()

    success = mix_podcast(
        voice_path=args.voice,
        output_path=args.output,
        intro_path=args.intro
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
