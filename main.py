import os
import sys
import time
import subprocess
import yt_dlp

# قائمة القنوات والمفاتيح المحددة
STREAMS = [
    {
        "channel_url": "https://kick.com/firas",
        "stream_key": "7swd-bmce-ym7w-5e2m-499u"
    },
    {
        "channel_url": "https://kick.com/Majah92",
        "stream_key": "re_11725544_eventa752cf60ea2c4cecbd8820b54335d0aa"
    }
]

RESTREAM_BASE_URL = "rtmp://live.restream.io/live/"

def get_stream_url(kick_url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'impersonate': 'chrome',  # لتخطي حظر Cloudflare / Kick 403
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(kick_url, download=False)
            return info.get('url', None)
    except Exception as e:
        print(f"[!] Primary extract error for {kick_url}: {e}")
        # محاولة احتياطية بدون خيار المحاكاة المباشر
        try:
            ydl_opts.pop('impersonate', None)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(kick_url, download=False)
                return info.get('url', None)
        except Exception as e2:
            print(f"[!] Fallback extract error: {e2}")
            return None

def start_stream():
    print("[*] Starting Kick Continuous Stream Bot...")
    
    live_url = None
    target_key = None
    
    for stream in STREAMS:
        print(f"[*] Checking live status for: {stream['channel_url']}...")
        url = get_stream_url(stream['channel_url'])
        if url:
            live_url = url
            target_key = stream['stream_key']
            print(f"[+] Found active stream on {stream['channel_url']}!")
            break

    if not live_url:
        print("[!] No active live streams found or channels are currently offline.")
        return

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
    
    subprocess.run(ffmpeg_cmd)

if __name__ == "__main__":
    start_stream()
