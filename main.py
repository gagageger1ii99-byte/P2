import os
import sys
import time
import subprocess
from curl_cffi import requests

STREAMS = [
    {
        "channel_name": "firas",
        "stream_key": "7swd-bmce-ym7w-5e2m-499u"
    },
    {
        "channel_name": "Majah92",
        "stream_key": "re_11725544_eventa752cf60ea2c4cecbd8820b54335d0aa"
    }
]

RESTREAM_BASE_URL = "rtmp://live.restream.io/live/"

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
        target_key = None
        
        for stream in STREAMS:
            channel = stream["channel_name"]
            print(f"[*] Checking live status for Kick channel: {channel}...")
            url = get_kick_stream_url(channel)
            if url:
                live_url = url
                target_key = stream["stream_key"]
                print(f"[+] Active stream found for {channel}!")
                break

        if not live_url:
            print("[!] No active live streams found. Retrying in 30 seconds...")
            time.sleep(30)
            continue

        full_restream_url = RESTREAM_BASE_URL + target_key

        print("[*] Launching FFmpeg to relay stream to Restream...")
        ffmpeg_cmd = [
            'ffmpeg',
            '-re',
            '-i', live_url,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-f', 'flv',
            full_restream_url
        ]
        
        # تشغيل FFmpeg، وفي حال التوقف يعيد السكربت المحاولة تلقائياً
        subprocess.run(ffmpeg_cmd)
        print("[!] FFmpeg process ended. Restarting check in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    start_stream()
