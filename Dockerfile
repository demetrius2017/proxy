# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем браузеры для Playwright
RUN python -m playwright install

# Копируем остальные файлы проекта
COPY . .

# Открываем порт 8080
EXPOSE 8080

# Запускаем приложение напрямую
CMD ["python", "main.py"]
