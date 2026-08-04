import os
import sys
import time
import subprocess
from threading import Thread
from curl_cffi import requests

STREAMS = [
    {
        "channel_name": "wolf",
        "rtmp_target": "rtmp://a.rtmp.youtube.com/live2/7swd-bmce-ym7w-5e2m-499u"
    },
    {
        "channel_name": "aymnalsatam",
        "rtmp_target": "rtmp://live.restream.io/live/re_11725544_event57b4ae7f7bef4493a9528d5432741a03"
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
        return None
    except Exception:
        return None

def handle_stream(stream):
    channel = stream["channel_name"]
    target_rtmp = stream["rtmp_target"]
    print(f"[*] Worker started for channel: {channel}")
    
    while True:
        live_url = get_kick_stream_url(channel)
        
        if not live_url:
            print(f"[-] Channel {channel} is offline. Retrying in 30 seconds...")
            time.sleep(30)
            continue

        print(f"[+] Active stream found for {channel}! Launching FFmpeg...")
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
        print(f"[!] FFmpeg ended for {channel}. Restarting check in 5 seconds...")
        time.sleep(5)

def start_bot():
    print("[*] Starting Multi-Stream Bot for all channels simultaneously...")
    threads = []
    
    for stream in STREAMS:
        t = Thread(target=handle_stream, args=(stream,))
        t.daemon = True
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()

if __name__ == "__main__":
    start_bot()
