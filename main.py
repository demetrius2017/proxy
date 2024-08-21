import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
from telegram import Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROXY_URL = os.getenv('PROXY_URL', 'https://www.easyproxy.tech/?__cpo=1')
YOUTUBE_URL = os.getenv('YOUTUBE_URL', 'https://www.youtube.com/')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7205474470:AAF5gNWm2mdtAJMbHa5Uj7LWg2y58sgI_NA')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://147.45.238.24/proxy.html')

async def get_proxy_url(url: str = YOUTUBE_URL) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            logger.info(f"Отправляем GET запрос на {PROXY_URL}")
            async with session.get(PROXY_URL) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')

            form = soup.find('form', id='request')
            csrf_token = form.find('input', {'name': 'csrf'})['value']
            logger.info(f"Найден CSRF-токен: {csrf_token[:10]}...")

            data = {
                'url': url,
                'csrf': csrf_token
            }
            logger.info(f"Отправляем POST запрос на {PROXY_URL}/requests")
            async with session.post(f"{PROXY_URL}/requests", data=data, allow_redirects=False) as response:
                if response.status in [301, 302, 303, 307, 308]:
                    long_url = response.headers['Location']
                    logger.info(f"Получена длинная ссылка: {long_url}")
                    return long_url
                else:
                    logger.warning("Не удалось получить длинную ссылку")
                    return None

    except Exception as e:
        logger.error(f"Произошла ошибка при получении прокси-ссылки: {str(e)}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Получена команда /start")
    try:
        long_url = await get_proxy_url(YOUTUBE_URL)

        if long_url:
            logger.info(f"Получена длинная ссылка: {long_url}")
            webapp_url = f"{WEBAPP_URL}?redirect_url={long_url}"
            await update.message.reply_text(
                "Нажмите кнопку ниже, чтобы открыть YouTube через наш прокси:",
                reply_markup={
                    "keyboard": [[{"text": "Открыть YouTube", "web_app": {"url": webapp_url}}]],
                    "resize_keyboard": True
                }
            )
        else:
            logger.warning("Не удалось получить прокси-ссылку, отправляем сообщение об ошибке")
            await update.message.reply_text(
                "Извините, не удалось получить прокси-ссылку. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.error(f"Произошла неожиданная ошибка: {str(e)}")
        await update.message.reply_text("Извините, произошла неожиданная ошибка. Пожалуйста, попробуйте позже.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()