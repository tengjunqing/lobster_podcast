#!/usr/bin/env python3
"""
播客混音脚本 v1.0
功能：片头拼接 + BGM背景音乐混合
用法：python3 mix_bgm.py <人声mp3> <输出mp3> [--bgm BGM路径] [--intro 片头路径]

混音逻辑：
- 片头部分：BGM音量30%（稍高，营造氛围）
- 正文部分：BGM音量15%（压低，不抢人声）
- 人声始终100%
"""

import subprocess
import sys
import os
import argparse

# 默认路径
PODCAST_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BGM = os.path.join(PODCAST_DIR, "assets", "podcast_bgm.mp3")
DEFAULT_INTRO = os.path.join(PODCAST_DIR, "assets", "intro.mp3")

# 音量参数
BGM_VOL_INTRO = 0.30   # 片头BGM音量（30%）
BGM_VOL_BODY = 0.15    # 正文BGM音量（15%）
VOICE_VOL = 1.0        # 人声音量（100%）


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


def mix_podcast(voice_path, output_path, bgm_path=None, intro_path=None):
    """
    混音流程：
    1. 拼接片头 + 正文人声
    2. 混合BGM（片头段高音量，正文段低音量）
    3. 输出最终音频
    """
    bgm_path = bgm_path or DEFAULT_BGM
    intro_path = intro_path or DEFAULT_INTRO

    # 检查文件
    for f, name in [(voice_path, "人声"), (bgm_path, "BGM"), (intro_path, "片头")]:
        if not os.path.exists(f):
            print(f"❌ {name}文件不存在: {f}")
            return False

    # 获取时长
    intro_dur = get_duration(intro_path)
    voice_dur = get_duration(voice_path)
    total_dur = intro_dur + voice_dur

    print(f"🎵 混音参数:")
    print(f"   片头: {intro_dur:.1f}s")
    print(f"   正文: {voice_dur:.1f}s")
    print(f"   总时长: {total_dur:.1f}s")
    print(f"   BGM音量 - 片头: {BGM_VOL_INTRO*100:.0f}%, 正文: {BGM_VOL_BODY*100:.0f}%")

    # FFmpeg 复杂滤镜：
    # 1. 拼接片头+人声为完整人声轨
    # 2. BGM循环播放，根据时间点调整音量（片头段高，正文段低）
    # 3. 混合两轨输出
    
    # 构建滤镜
    # [0:a] = 片头, [1:a] = 正文人声, [2:a] = BGM
    filter_complex = (
        # 拼接片头+人声
        f"[0:a][1:a]concat=n=2:v=0:a=1[voice];"
        # BGM循环到足够长
        f"[2:a]aloop=loop=-1:size=2e+09,atrim=duration={total_dur}[bgm_loop];"
        # BGM音量控制：片头段30%，正文段15%
        f"[bgm_loop]volume=enable='between(t,0,{intro_dur})':volume={BGM_VOL_INTRO},"
        f"volume=enable='gte(t,{intro_dur})':volume={BGM_VOL_BODY},"
        # 淡入淡出
        f"afade=t=in:st=0:d=1,afade=t=out:st={total_dur-2}:d=2[bgm_mixed];"
        # 混合人声和BGM
        f"[voice][bgm_mixed]amix=inputs=2:duration=first:dropout_transition=3[out]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", intro_path,      # 输入0: 片头
        "-i", voice_path,      # 输入1: 正文人声
        "-i", bgm_path,        # 输入2: BGM
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
    parser = argparse.ArgumentParser(description="播客混音（片头+BGM+人声）")
    parser.add_argument("voice", help="人声音频路径")
    parser.add_argument("output", help="输出音频路径")
    parser.add_argument("--bgm", default=DEFAULT_BGM, help="BGM路径")
    parser.add_argument("--intro", default=DEFAULT_INTRO, help="片头路径")

    args = parser.parse_args()

    success = mix_podcast(
        voice_path=args.voice,
        output_path=args.output,
        bgm_path=args.bgm,
        intro_path=args.intro
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
