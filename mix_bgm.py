#!/usr/bin/env python3
"""
播客混音脚本 v2.0
功能：片头音乐与人声重叠（看点预告）+ BGM铺底 + 片尾音乐
用法：python3 mix_bgm.py <人声mp3> <输出mp3> [--bgm BGM路径] [--intro 片头路径] [--outro 片尾路径]

混音逻辑（v2.0 - 看点预告模式）：
- 片头段：片头音乐100% + 人声（精彩看点预告，音乐与人声重叠）
- 片头结束后：片头音乐渐弱到15%，BGM开始铺底（15%）
- 正文段：BGM 15% + 人声
- 片尾段：片尾音乐100%
"""

import subprocess
import sys
import os
import argparse

# 默认路径
PODCAST_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BGM = os.path.join(PODCAST_DIR, "assets", "podcast_bgm.mp3")
DEFAULT_INTRO = os.path.join(PODCAST_DIR, "assets", "Intro music.mp3")
DEFAULT_OUTRO = None  # 片尾音乐已禁用

# 音量参数
INTRO_VOL = 0.8        # 片头音乐音量（80%）
BGM_VOL_BODY = 0.8    # 正文BGM音量（80%）
VOICE_VOL = 1.2        # 人声音量（120%，加强20%）
INTRO_OVERLAP = 25     # 片头音乐与人声重叠时长（秒），覆盖到"大家好"前
OUTRO_ADVANCE = 30     # 片尾音乐提前进入时长（秒），在"我们明天见"前进入


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


def mix_podcast(voice_path, output_path, bgm_path=None, intro_path=None, outro_path=None):
    """
    混音流程：
    1. 片头音乐与人声重叠（精彩看点预告效果）
    2. 片头音乐渐弱后，BGM铺底
    3. 片尾音乐收尾
    """
    bgm_path = bgm_path or DEFAULT_BGM
    intro_path = intro_path or DEFAULT_INTRO
    outro_path = outro_path or DEFAULT_OUTRO

    # 检查文件
    for f, name in [(voice_path, "人声"), (bgm_path, "BGM"), (intro_path, "片头")]:
        if not os.path.exists(f):
            print(f"❌ {name}文件不存在: {f}")
            return False
    has_outro = outro_path and os.path.exists(outro_path)
    if not has_outro:
        print(f"⚠️ 片尾音乐不存在，将跳过: {outro_path}")

    # 获取时长
    intro_dur = get_duration(intro_path)
    voice_dur = get_duration(voice_path)
    outro_dur = get_duration(outro_path) if has_outro else 0
    body_dur = voice_dur  # 人声总时长 = 看点预告 + 正文
    overlap = min(INTRO_OVERLAP, intro_dur)
    total_dur = overlap + body_dur + outro_dur

    print(f"🎵 混音参数（看点预告模式）:")
    print(f"   片头音乐: {overlap:.0f}s（与人声重叠，在'大家好'前结束）")
    print(f"   人声: {body_dur:.1f}s")
    if has_outro:
        print(f"   片尾音乐: {outro_dur:.1f}s")
    print(f"   总时长: {total_dur:.1f}s")
    print(f"   🎤 片头段: 音乐{INTRO_VOL*100:.0f}% + 人声（精彩看点）")
    print(f"   🎵 正文段: BGM {BGM_VOL_BODY*100:.0f}% + 人声")
    if has_outro:
        print(f"   🎵 片尾段: 音乐100%")

    # 构建滤镜 - 片头音乐与人声重叠（看点预告效果）
    # [0:a]=片头音乐 [1:a]=人声 [2:a]=片尾(可选) [3:a]=BGM
    if has_outro:
        outro_start = overlap + body_dur - OUTRO_ADVANCE
        filter_complex = (
            # 片头音乐：前 overlap 秒高音量（与人声重叠=看点预告），之后静音
            f"[0:a]atrim=duration={overlap},volume={INTRO_VOL},"
            f"afade=t=out:st={overlap-1.5}:d=1.5[intro_vol];"
            # 人声音量增强20%
            f"[1:a]volume={VOICE_VOL}[voice_vol];"
            # BGM循环，正文段音量，片头段静音，添加淡入淡出（1.5秒）
            f"[3:a]aloop=loop=-1:size=2e+09,atrim=duration={total_dur},"
            f"volume=if(lt(t\\,{overlap})\\,0\\,{BGM_VOL_BODY}),"
            f"afade=t=in:st={overlap}:d=1.5,afade=t=out:st={total_dur-1.5}:d=1.5[bgm_vol];"
            # 片尾音乐：先创建静音段，再拼接片尾，实现延迟播放
            f"anullsrc=r=44100:cl=mono,atrim=duration={outro_start}[silence];"
            f"[silence][2:a]concat=n=2:v=0:a=1[outro_padded];"
            f"[outro_padded]atrim=duration={total_dur},"
            f"volume=1.5,"
            f"afade=t=in:st={outro_start}:d=1,afade=t=out:st={outro_start+outro_dur-2}:d=2[outro_vol];"
            # 混合4层：片头音乐 + 人声 + BGM + 片尾音乐
            f"[intro_vol][voice_vol][bgm_vol][outro_vol]amix=inputs=4:duration=longest:dropout_transition=0[out]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", intro_path,
            "-i", voice_path,
            "-i", outro_path,
            "-i", bgm_path,
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-c:a", "libmp3lame",
            "-b:a", "128k",
            "-ar", "44100",
            "-ac", "1",
            output_path
        ]
    else:
        filter_complex = (
            f"[0:a]atrim=duration={overlap},volume={INTRO_VOL},"
            f"afade=t=out:st={overlap-1.5}:d=1.5[intro_vol];"
            f"[1:a]volume={VOICE_VOL}[voice_vol];"
            f"[2:a]aloop=loop=-1:size=2e+09,atrim=duration={total_dur},"
            f"volume=if(lt(t\\,{overlap})\\,0\\,{BGM_VOL_BODY})[bgm_vol];"
            f"[intro_vol][voice_vol][bgm_vol]amix=inputs=3:duration=longest:dropout_transition=0[out]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", intro_path,
            "-i", voice_path,
            "-i", bgm_path,
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
    parser = argparse.ArgumentParser(description="播客混音（看点预告模式：片头音乐+人声重叠+BGM+片尾）")
    parser.add_argument("voice", help="人声音频路径")
    parser.add_argument("output", help="输出音频路径")
    parser.add_argument("--bgm", default=DEFAULT_BGM, help="BGM路径")
    parser.add_argument("--intro", default=DEFAULT_INTRO, help="片头路径")
    parser.add_argument("--outro", default=DEFAULT_OUTRO, help="片尾路径")

    args = parser.parse_args()

    success = mix_podcast(
        voice_path=args.voice,
        output_path=args.output,
        bgm_path=args.bgm,
        intro_path=args.intro,
        outro_path=args.outro
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
