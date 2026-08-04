import os
import sys
import time
import subprocess
from curl_cffi import requests

# إعداد القنوات وتحديد السيرفر المناسب لكل مفتاح
STREAMS = [
    {
        "channel_name": "firas",
        "rtmp_target": "rtmp://a.rtmp.youtube.com/live2/7swd-bmce-ym7w-5e2m-499u"
    },
    {
        "channel_name": "majah92",
        "rtmp_target": "rtmp://live.restream.io/live/re_11725544_eventa752cf60ea2c4cecbd8820b54335d0aa"
    }
]

def get_kick_stream_url(channel_name):
    api_url = f"https://kick.com/api/v2/channels/{channel_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    
    try:
        response = requests.get(api_url, headers=headers, impersonate="chrome120", timeout=15)
        if response.status_code == 200:
            data = response.json()
            playback_url = data.get("playback_url")
            if playback_url:
                return playback_url
            else:
                print(f"[-] Channel {channel_name} is currently offline.")
        else:
            print(f"[!] API Error {response.status_code} for channel {channel_name}")
    except Exception as e:
        print(f"[!] Request Exception for {channel_name}: {e}")
        
    return None

def start_stream():
    print("[*] Starting Kick Continuous Stream Bot...")
    
    while True:
        live_url = None
        target_rtmp = None
        active_channel = None
        
        for stream in STREAMS:
            channel = stream["channel_name"]
            print(f"[*] Checking live status for Kick channel: {channel}...")
            url = get_kick_stream_url(channel)
            if url:
                live_url = url
                target_rtmp = stream["rtmp_target"]
                active_channel = channel
                print(f"[+] Active stream found for {channel}!")
                break

        if not live_url:
            print("[!] No active live streams found. Retrying in 30 seconds...")
            time.sleep(30)
            continue

        print(f"[*] Launching FFmpeg to relay stream from {active_channel}...")
        ffmpeg_cmd = [
            'ffmpeg',
            '-re',
            '-i', live_url,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-f', 'flv',
            target_rtmp
        ]
        
        subprocess.run(ffmpeg_cmd)
        print("[!] FFmpeg process ended. Restarting check in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    start_stream()
