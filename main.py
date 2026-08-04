import os
import time
import subprocess
from curl_cffi import requests

# معلومات قناة وولف (تذهب إلى يوتيوب)
CHANNEL_1 = "wolf"
RTMP_TARGET_1 = "rtmp://a.rtmp.youtube.com/live2/7swd-bmce-ym7w-5e2m-499u"

# معلومات قناة أيمن (تذهب إلى ريستريم)
CHANNEL_2 = "aymnalsatam"
RTMP_TARGET_2 = "rtmp://live.restream.io/live/re_11725544_eventa752cf60ea2c4cecbd8820b54335d0aa"

def get_kick_stream_url(channel_name):
    api_url = f"https://kick.com/api/v2/channels/{channel_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://kick.com/",
        "Origin": "https://kick.com/"
    }
    try:
        response = requests.get(api_url, headers=headers, impersonate="chrome120", timeout=15)
        if response.status_code == 200:
            data = response.json()
            playback_url = data.get("playback_url")
            if playback_url:
                return playback_url
    except Exception:
        pass
    return None

def run_bridge(channel_name, rtmp_target):
    print(f"[*] Starting Stream Bridge for: {channel_name}...")
    
    while True:
        live_url = get_kick_stream_url(channel_name)
        
        if not live_url:
            print(f"[!] Stream for {channel_name} is offline. Retrying in 30 seconds...")
            time.sleep(30)
            continue

        print(f"[+] Active stream found for {channel_name}! Launching FFmpeg...")
        
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-fflags', '+nobuffer+discardcorrupt',
            '-i', live_url,
            '-map', '0:v:0',
            '-map', '0:a:0?',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'flv',
            rtmp_target
        ]
        
        process = subprocess.Popen(ffmpeg_cmd)
        process.wait()
        print(f"[!] FFmpeg connection dropped for {channel_name}. Re-checking in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    import threading
    
    # تشغيل القناتين معاً بالتوازي
    t1 = threading.Thread(target=run_bridge, args=(CHANNEL_1, RTMP_TARGET_1))
    t2 = threading.Thread(target=run_bridge, args=(CHANNEL_2, RTMP_TARGET_2))
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
