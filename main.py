import os
import time
import threading

# ------------ الإعدادات ------------

# --- القناة الأولى (Kick -> Restream) ---
KICK_CHANNEL_1 = "اسم_القناة_الأولى"
RESTREAM_KEY = ""  # مفتاح Restream فارغ حالياً
URL_RESTREAM = f"rtmp://live.restream.io/live/{RESTREAM_KEY}"

# --- القناة الثانية (Kick -> YouTube) ---
KICK_CHANNEL_2 = "Majah92"
YOUTUBE_KEY = "7swd-bmce-ym7w-5e2m-499u"
URL_YOUTUBE = f"rtmp://a.rtmp.youtube.com/live2/{YOUTUBE_KEY}"


# ------------ دالة مراقبة ونقل البث ------------
def stream_worker(kick_channel, target_url, platform_name):
    print(f"[*] Started monitoring [{kick_channel}] for {platform_name}...")
    while True:
        try:
            # التأكد من وجود رابط البث أولاً إذا كان الكي متوفراً
            if "rtmp://" in target_url and target_url.endswith("/"):
                print(f"[!] Warning: Key for {platform_name} is empty. Retrying in 30s...")
                time.sleep(30)
                continue

            stream = os.popen(f'yt-dlp -g "https://kick.com/{kick_channel}"').read().strip()
            
            if "http" in stream:
                print(f"[+] [{kick_channel}] LIVE! Transmitting to {platform_name}...")
                cmd = (
                    f'ffmpeg -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
                    f'-i "{stream}" -c:v copy -c:a aac -b:a 128k -ar 44100 '
                    f'-f flv "{target_url}"'
                )
                os.system(cmd)
                print(f"[-] [{kick_channel}] Stream disconnected. Re-checking in 10s...")
            else:
                time.sleep(15)
        except Exception as e:
            print(f"[!] Error in {kick_channel} ({platform_name}): {e}")
            time.sleep(15)


# ------------ تشغيل القناتين بالتوازي (Threads) ------------
t1 = threading.Thread(target=stream_worker, args=(KICK_CHANNEL_1, URL_RESTREAM, "Restream"))
t2 = threading.Thread(target=stream_worker, args=(KICK_CHANNEL_2, URL_YOUTUBE, "YouTube"))

t1.start()
t2.start()
