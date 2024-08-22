# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем браузеры Playwright
RUN apt-get update && apt-get install -y libnss3 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libglib2.0-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxrandr2 libasound2 libpangocairo-1.0-0 libpango-1.0-0 libjpeg-dev libx11-xcb-dev
RUN python -m playwright install --with-deps

# Копируем остальные файлы проекта
COPY . .

# Открываем порт 8080
EXPOSE 8080

# Запускаем бота
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]
