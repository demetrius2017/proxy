import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import subprocess
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROXY_URL = 'https://www.easyproxy.tech' # URL прокси-сервера
YOUTUBE_URL = 'https://www.youtube.com/'
TOKEN = '6740830002:AAFcw7PqsWgGp4cJna24vofPtU1P2dCT4yE'
WORKER_URL = 'https://green-king-173c.nazarov-dubai.workers.dev/'

async def get_actual_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Открыть YouTube", web_app=WebAppInfo(url=WORKER_URL))]
    ])
    await update.message.reply_text(
        "Нажмите на кнопку ниже, чтобы открыть YouTube через наш прокси.",
        reply_markup=keyboard
    )

def install_playwright_browsers():
    logger.info("Устанавливаем браузеры Playwright...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)


async def _get_actual_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Запрос на получение актуальной ссылки")
    message = await update.message.reply_text("Запрашиваем подходящий сервер...")

    # Запускаем анимацию загрузки
    loading_task = asyncio.create_task(animate_loading(message, "Запрашиваем подходящий сервер"))

    try:
        proxy_url = await get_proxy_url(YOUTUBE_URL)
    finally:
        # Останавливаем анимацию загрузки
        loading_task.cancel()

    if proxy_url:
        logger.info(f"Получена прокси-ссылка: {proxy_url}")
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Открыть YouTube", web_app=WebAppInfo(url=proxy_url))]
        ])
        await message.edit_text(
            "Вот ваша актуальная ссылка для доступа к YouTube. Нажмите на кнопку ниже, чтобы открыть YouTube через наш прокси.",
            reply_markup=keyboard
        )
    else:
        logger.warning("Не удалось получить прокси-ссылку")
        await message.edit_text(
            "Извините, не удалось получить прокси-ссылку. Пожалуйста, попробуйте позже."
        )

async def get_proxy_url(url: str = YOUTUBE_URL) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            # Шаг 1: Получаем начальную страницу
            logger.info(f"Отправляем GET запрос на {PROXY_URL}")
            async with session.get(PROXY_URL) as response:
                text = await response.text()
                logger.info(f"Получен ответ (первые 1000 символов):\n{text[:1000]}")
                
                soup = BeautifulSoup(text, 'html.parser')

            # Шаг 2: Ищем форму и извлекаем CSRF-токен
            form = soup.find('form', id='request')
            if not form:
                logger.error("Форма с id 'request' не найдена")
                return None
            
            csrf_input = form.find('input', {'name': 'csrf'})
            if not csrf_input:
                logger.error("Input с именем 'csrf' не найден")
                return None
            
            csrf_token = csrf_input['value']
            logger.info(f"Найден CSRF-токен: {csrf_token}")

            # Шаг 3: Отправляем POST-запрос
            data = {
                'url': url,
                'csrf': csrf_token
            }
            logger.info(f"Отправляем POST запрос на {PROXY_URL}/requests с данными: {data}")
            async with session.post(f"{PROXY_URL}/requests", data=data, allow_redirects=False) as response:
                logger.info(f"Статус ответа: {response.status}")
                if response.status in [301, 302, 303, 307, 308]:
                    location = response.headers['Location']
                    logger.info(f"Получен редирект на: {location}")
                    return location
                else:
                    text = await response.text()
                    logger.info(f"Получен ответ (первые 1000 символов):\n{text[:1000]}")
                    soup = BeautifulSoup(text, 'html.parser')
                    meta_refresh = soup.find('meta', {'http-equiv': 'refresh'})
                    if meta_refresh:
                        content = meta_refresh['content']
                        url = content.split('url=')[1]
                        logger.info(f"Найден meta refresh. URL: {url}")
                        return url
                    else:
                        logger.warning("Meta refresh не найден")
                        return str(response.url)

    except Exception as e:
        logger.error(f"Произошла ошибка при получении прокси-ссылки: {str(e)}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Получена команда /start")
    try:
        proxy_url = await get_proxy_url(YOUTUBE_URL)

        if proxy_url:
            logger.info(f"Отправляем сообщение с кнопкой, содержащей прокси-ссылку: {proxy_url}")
            message_text = (
                "Нажмите кнопку ниже, чтобы открыть YouTube через наш прокси:\n\n"
                f"Используемая ссылка: {proxy_url}"
            )
            await update.message.reply_text(
                message_text,
                reply_markup={
                    "keyboard": [[{"text": "Открыть YouTube", "web_app": {"url": proxy_url}}]],
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


async def animate_loading(message, text):
    dots = ["⋅", "•", "●"]
    i = 0
    while True:
        await message.edit_text(f"{text} {dots[i % 3]}{dots[(i + 1) % 3]}{dots[(i + 2) % 3]}")
        i += 1
        await asyncio.sleep(0.5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Получена команда /start")
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Получить актуальную ссылку")]], resize_keyboard=True)
    await update.message.reply_text(
        "Добро пожаловать! Нажмите кнопку ниже, чтобы получить актуальную ссылку на прокси.",
        reply_markup=keyboard
    )


def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^Получить актуальную ссылку$"), get_actual_link))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
