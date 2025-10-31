# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (optional, kept tiny)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Spaces set PORT; default to 7860 for local runs
ENV PORT=7860

EXPOSE 7860
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860", "--proxy-headers"]
