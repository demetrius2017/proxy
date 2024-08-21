import aiohttp
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import subprocess
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROXY_URL = 'https://www.easyproxy.tech/?__cpo=1'
YOUTUBE_URL = 'https://www.youtube.com/'
TOKEN = '7205474470:AAF5gNWm2mdtAJMbHa5Uj7LWg2y58sgI_NA'


def install_playwright_browsers():
    logger.info("Устанавливаем браузеры Playwright...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)


async def get_proxy_url(url: str = YOUTUBE_URL) -> str:
    try:
        # Шаг 1: Получение длинной ссылки
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
                else:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    meta_refresh = soup.find('meta', {'http-equiv': 'refresh'})
                    if meta_refresh:
                        content = meta_refresh['content']
                        long_url = content.split('url=')[1]
                        logger.info(f"Получена длинная ссылка из meta refresh: {long_url}")
                    else:
                        long_url = str(response.url)
                        logger.info(f"Используем URL ответа как длинную ссылку: {long_url}")

        # Шаг 2: Обработка длинной ссылки с помощью Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            logger.info(f"Открываем длинную ссылку в браузере")
            await page.goto(long_url)

            # Ждем, пока страница загрузится
            await page.wait_for_load_state('networkidle', timeout=60000)

            current_url = page.url
            logger.info(f"Текущий URL после загрузки: {current_url}")

            # Пытаемся найти короткую ссылку
            try:
                short_url_element = await page.wait_for_selector('input#short-url', timeout=30000)
                if short_url_element:
                    short_url = await short_url_element.get_attribute('value')
                    logger.info(f"Найдена короткая ссылка: {short_url}")
                    await browser.close()
                    return short_url
            except:
                logger.warning("Не удалось найти короткую ссылку на странице")

            # Если короткая ссылка не найдена, возвращаем текущий URL
            logger.info(f"Возвращаем текущий URL как прокси-ссылку: {current_url}")
            await browser.close()
            return current_url

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


async def get_actual_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Запрос на получение актуальной ссылки")
    message = await update.message.reply_text("Запрашиваем подходящий сервер...")

    # Запускаем анимацию загрузки
    loading_task = asyncio.create_task(animate_loading(message, "Запрашиваем подходящий сервер"))

    try:
        # x = await get_proxy_url(YOUTUBE_URL)
        # proxy_url = "https://easyproxy.tech/?__cpo=aHR0cHM6Ly93d3cueW91dHViZS5jb20"
        # Получаем прокси-ссылку
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


def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^Получить актуальную ссылку$"), get_actual_link))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
