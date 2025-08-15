# ./Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ابزار لازم (برای صبر تا DB آماده شود)
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# نصب وابستگی‌ها
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# اسکریپت ورود
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# فقط کد Django را کپی کن (پوشه‌ای که هم manage.py دارد هم پوشه core/)
# نتیجه: /app/manage.py و /app/core/ ساخته می‌شود
COPY core/ /app/

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
