#!/usr/bin/env python3
"""
小米 MiMo-v2.5-tts 语音合成脚本 v2.0
新增：集成音频后处理（降噪+响度标准化+ID3嵌入）
用法：python3 mimo_tts.py "要转换的文本" 输出文件路径.mp3 [--title TITLE]
"""

import sys
import json
import base64
import requests
import os
import subprocess

API_URL = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"
API_KEY = "tp-cxcgsq8xgq26snnfqcj8yxi0no81oo1glxb2eukglwvvmtzk"
MODEL = "mimo-v2.5-tts"

# 后处理脚本路径
POSTPROCESS_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_postprocess.py")


def generate_speech(text, output_path, voice_prompt="你是一个专业的播客主播，语速适中，发音清晰", title=None):
    """调用 MiMo TTS 生成语音，并进行后处理"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # MiMo TTS 格式：user 角色放提示词，assistant 角色放要转语音的文本
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": voice_prompt},
            {"role": "assistant", "content": text}
        ],
        "stream": False
    }

    print(f"🎤 调用 MiMo TTS API...")
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=300)
    resp.raise_for_status()

    data = resp.json()

    # 提取 base64 音频数据
    audio_b64 = data["choices"][0]["message"]["audio"]["data"]
    audio_bytes = base64.b64decode(audio_b64)

    # 保存为临时 wav 文件
    raw_wav_path = output_path.replace(".mp3", "_raw.wav")
    with open(raw_wav_path, "wb") as f:
        f.write(audio_bytes)

    raw_size_kb = len(audio_bytes) / 1024
    print(f"📥 原始音频: {raw_size_kb:.1f}KB (WAV)")

    # 后处理：降噪 + 响度标准化 + ID3嵌入
    if os.path.exists(POSTPROCESS_SCRIPT):
        print(f"🔧 执行音频后处理...")
        cmd = [
            "python3", POSTPROCESS_SCRIPT,
            raw_wav_path,
            output_path,
        ]
        if title:
            cmd.extend(["--title", title])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        print(result.stdout)

        # 清理临时文件
        if os.path.exists(output_path):
            os.remove(raw_wav_path)
        else:
            # 后处理失败，回退到简单转换
            print("⚠️ 后处理失败，回退到简单转换...")
            os.system(f'ffmpeg -y -i "{raw_wav_path}" -codec:a libmp3lame -b:a 128k "{output_path}" 2>/dev/null')
            if os.path.exists(output_path):
                os.remove(raw_wav_path)
    else:
        # 后处理脚本不存在，简单转换
        print(f"⚠️ 后处理脚本不存在，使用简单转换...")
        os.system(f'ffmpeg -y -i "{raw_wav_path}" -codec:a libmp3lame -b:a 128k "{output_path}" 2>/dev/null')
        if os.path.exists(output_path):
            os.remove(raw_wav_path)

    if os.path.exists(output_path):
        size_kb = os.path.getsize(output_path) / 1024
        print(f"✅ 语音生成成功：{output_path} ({size_kb:.1f}KB)")
    else:
        print(f"❌ 语音生成失败")
        return None

    return output_path


def main():
    if len(sys.argv) < 3:
        print("用法: python3 mimo_tts.py '文本内容' 输出路径.mp3 [--title 标题]")
        sys.exit(1)

    text = sys.argv[1]
    output = sys.argv[2]

    # 解析可选参数
    title = None
    if "--title" in sys.argv:
        idx = sys.argv.index("--title")
        if idx + 1 < len(sys.argv):
            title = sys.argv[idx + 1]

    generate_speech(text, output, title=title)


if __name__ == "__main__":
    main()
