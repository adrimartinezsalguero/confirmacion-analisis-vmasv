FROM python:3.11-slim

# Instalar Chromium directamente desde apt + todas las dependencias necesarias
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    fonts-liberation \
    fonts-noto-color-emoji \
    libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 \
    libcups2t64 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 libasound2t64 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Decirle a Playwright que use el Chromium del sistema, no el suyo
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright SIN dependencias (ya las tenemos instaladas arriba)
RUN playwright install chromium

COPY skool_bot.py .

CMD ["python", "skool_bot.py"]
