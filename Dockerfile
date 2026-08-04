FROM python:3.10-slim

# تثبيت ffmpeg والأدوات الأساسية
RUN apt-get update && apt-get install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ الملفات وتثبيت مكتبات بايثون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# تشغيل السكربت
CMD ["python", "main.py"]

