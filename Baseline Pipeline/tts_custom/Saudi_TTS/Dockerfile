# ====== المرحلة الأولى: بيئة Python أساسية ======
FROM python:3.10-slim AS base

# إعداد المتغيرات البيئية
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملفات المتطلبات
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ بقية المشروع
COPY . .

# ====== الأمر الافتراضي للتشغيل ======
CMD ["python", "tests/smoke_test_whisper.py"]
