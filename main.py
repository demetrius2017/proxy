import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Замените на свой токен
TOKEN = "6740830002:AAFcw7PqsWgGp4cJna24vofPtU1P2dCT4yE"

# Обновленный URL вашего Web App (без HTTPS, так как у нас пока нет SSL)
WEBAPP_URL = "http://94.241.174.212"

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение с кнопкой для запуска Web App."""
    await update.message.reply_text(
        "Добро пожаловать! Нажмите кнопку ниже, чтобы открыть Proxy App Launcher:",
        reply_markup={
            "keyboard": [[{"text": "Start Proxy App Launcher", "web_app": {"url": WEBAPP_URL}}]],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
    )


def main() -> None:
    """Запускает бота и веб-сервер."""

    # Настройка и запуск Telegram бота
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    main()