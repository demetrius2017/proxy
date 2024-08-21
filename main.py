import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = '6740830002:AAFcw7PqsWgGp4cJna24vofPtU1P2dCT4yE'
PROXY_PAGE_URL = 'http://147.45.238.24/proxy.html'  # Обновлено с redirect.html на proxy.html

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Получена команда /start")
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Открыть YouTube через прокси")]], resize_keyboard=True)
    await update.message.reply_text(
        "Добро пожаловать! Нажмите кнопку ниже, чтобы открыть YouTube через наш прокси.",
        reply_markup=keyboard
    )

async def open_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Запрос на открытие YouTube через прокси")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Открыть YouTube", url=PROXY_PAGE_URL)]
    ])
    await update.message.reply_text(
        "Нажмите на кнопку ниже, чтобы открыть YouTube через наш прокси.",
        reply_markup=keyboard
    )

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^Открыть YouTube через прокси$"), open_youtube))
    application.run_polling()

if __name__ == '__main__':
    main()