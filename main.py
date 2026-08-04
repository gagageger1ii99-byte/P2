import os
import sys
import time
import subprocess
import yt_dlp

# قائمة بالروابط أو الخيارات الأساسية
RESTREAM_URL = os.getenv("RESTREAM_URL", "")

def get_stream_url(youtube_url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        # تم تصحيح هدف المحاكاة للتوافق مع curl_cffi أو إزالته لتفادي الخطأ
        'impersonate': 'chrome-110',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            return info.get('url', None)
    except Exception as e:
        print(f"[!] Error extracting stream URL: {e}")
        # تجربة الاستخراج بدون impersonate في حال الفشل
        try:
            ydl_opts.pop('impersonate', None)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                return info.get('url', None)
        except Exception as e2:
            print(f"[!] Fallback error: {e2}")
            return None

def start_stream():
    print("[*] Starting Continuous Stream Bot...")
    # يرجى وضع رابط البث أو التغذية المطلوبة هنا
    stream_source = "https://www.youtube.com/watch?v=live_stream_id" 
    
    url = get_stream_url(stream_source)
    if not url:
        print("[!] Could not retrieve stream URL.")
        return

    print("[*] Stream URL retrieved successfully. Launching FFmpeg...")
    # خيارات FFmpeg الموصى بها للبث المستمر
    ffmpeg_cmd = [
        'ffmpeg',
        '-re',
        '-i', url,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-f', 'flv',
        RESTREAM_URL
    ]
    
    subprocess.run(ffmpeg_cmd)

if __name__ == "__main__":
    start_stream()
