import aiohttp
import base64
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

PROXY_URL = 'https://www.easyproxy.tech'
YOUTUBE_URL = 'https://2ip.ru'
TOKEN = '6740830002:AAFcw7PqsWgGp4cJna24vofPtU1P2dCT4yE'


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
            # Открываем браузер в headless режиме (без интерфейса)
            browser = await p.chromium.launch(headless=True)

            # Устанавливаем заголовки (включая User-Agent и другие стандартные заголовки)
            iphone_user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
            page = await browser.new_page(
                user_agent=iphone_user_agent,
                extra_http_headers={
                    "Referer": "https://www.google.com",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                }
            )

            # Переходим по длинной ссылке
            await page.goto(url)

            # Ждем полной загрузки страницы и исполнения всех скриптов
            await page.wait_for_load_state('networkidle', timeout=60000)

            # Проверяем содержимое страницы каждые 2 секунды
            is_launching = True
            while is_launching:
                # Проверяем текущий URL и содержимое страницы
                current_url = page.url
                logger.info(f"Текущий URL: {current_url}")

                page_content = await page.content()
                logger.info(f"Содержимое страницы: {page_content[:500]}")  # Логируем первые 500 символов

                # Если "Proxy is launching..." больше не отображается, завершаем ожидание
                if "Proxy is launching..." not in page_content:
                    is_launching = False
                else:
                    await asyncio.sleep(2)

            # Получаем итоговый URL
            proxy_link = page.url
            logger.info(f"Ключ зарегестрирован: {proxy_link}")

            await browser.close()
            return proxy_link


    except Exception as e:
        logger.error(f"Произошла ошибка при получении прокси-ссылки: {str(e)}")
        return None


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


# Функция для кодирования URL в Base64
def encode_url(url: str) -> str:
    return base64.b64encode(url.encode('utf-8')).decode('utf-8')

# Обновленная функция для получения ссылок и создания кнопок
async def get_actual_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    install_playwright_browsers()
    logger.info("Запрос на получение актуальной ссылки")
    message = await update.message.reply_text("Запрашиваем подходящий сервер...")

    # Запускаем анимацию загрузки
    loading_task = asyncio.create_task(animate_loading(message, "Запрашиваем подходящий сервер"))

    try:
        # Получаем прокси-ссылку (тестируем на одном URL, например, YouTube)
        proxy_url = await get_proxy_url(YOUTUBE_URL)
    finally:
        # Останавливаем анимацию загрузки
        loading_task.cancel()

    if proxy_url:
        logger.info(f"Получена прокси-ссылка: {proxy_url}")
        
        # Сайты, которые нужно закодировать и сделать кнопками
        sites = {
            "YouTube": "https://www.youtube.com",
            "Facebook": "https://www.facebook.com",
            "2IP": "https://www.2ip.ru",
            "TikTok": "https://www.tiktok.com",
            "Instagram": "https://www.instagram.com"
        }
        
        # Генерация кнопок с закодированными ссылками
        buttons = [
            [InlineKeyboardButton(f"Открыть {name}", web_app=WebAppInfo(url=f"https://easyproxy.tech/?__cpo={encode_url(url)}"))]
            for name, url in sites.items()
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        # Отправляем сообщение с кнопками для всех сайтов
        await message.edit_text(
            "Нажмите на одну из кнопок ниже, чтобы открыть сайт через наш прокси.",
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
