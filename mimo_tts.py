#!/usr/bin/env python3
"""
小米 MiMo-v2.5-tts 语音合成脚本
用法：python3 mimo_tts.py "要转换的文本" 输出文件路径.mp3
"""

import sys
import json
import base64
import requests
import os

API_URL = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"
API_KEY = "tp-cxcgsq8xgq26snnfqcj8yxi0no81oo1glxb2eukglwvvmtzk"
MODEL = "mimo-v2.5-tts"


def generate_speech(text, output_path, voice_prompt="你是一个专业的播客主播，语速适中，发音清晰"):
    """调用 MiMo TTS 生成语音"""
    
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
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    
    data = resp.json()
    
    # 提取 base64 音频数据
    audio_b64 = data["choices"][0]["message"]["audio"]["data"]
    audio_bytes = base64.b64decode(audio_b64)
    
    # 保存为 wav 文件（MiMo 返回的是 WAV 格式）
    wav_path = output_path.replace(".mp3", ".wav")
    with open(wav_path, "wb") as f:
        f.write(audio_bytes)
    
    # 用 ffmpeg 转换为 mp3
    mp3_path = output_path
    os.system(f'ffmpeg -y -i "{wav_path}" -codec:a libmp3lame -b:a 128k "{mp3_path}" 2>/dev/null')
    
    # 清理 wav 文件
    if os.path.exists(mp3_path):
        os.remove(wav_path)
    
    size_kb = os.path.getsize(mp3_path) / 1024
    print(f"✅ 语音生成成功：{mp3_path} ({size_kb:.1f}KB)")
    return mp3_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 mimo_tts.py '文本内容' 输出路径.mp3")
        sys.exit(1)
    
    text = sys.argv[1]
    output = sys.argv[2]
    generate_speech(text, output)
