import time
import base64
import requests
import logging
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROXY_URL = 'https://www.easyproxy.tech'
YOUTUBE_URL = 'https://2ip.ru'
TOKEN = '6740830002:AAFcw7PqsWgGp4cJna24vofPtU1P2dCT4yE'

# Словарь для хранения информации о токенах и времени обновления для каждого IP
ip_token_cache = {}

# Время жизни токена (например, 3 часа)
TOKEN_LIFETIME = 3 * 60 * 60


# Функция для получения публичного IP пользователя с обработкой ошибок
def get_public_ip() -> str:

        return None

# Функция для кодирования URL в Base64
def encode_url(url: str) -> str:
    return base64.b64encode(url.encode('utf-8')).decode('utf-8')

# Функция для регистрации токена через Playwright и возврата прокси-ссылки
async def register_token_for_ip(ip: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            logger.info(f"Регистрация токена для IP {ip}")
            async with session.get(PROXY_URL) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')

            form = soup.find('form', id='request')
            csrf_token = form.find('input', {'name': 'csrf'})['value']

            data = {'url': YOUTUBE_URL, 'csrf': csrf_token}
            async with session.post(f"{PROXY_URL}/requests", data=data, allow_redirects=False) as response:
                if response.status in [301, 302, 303, 307, 308]:
                    long_url = response.headers['Location']
                else:
                    long_url = str(response.url)

        # Используем Playwright для завершения процесса
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            iphone_user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
            page = await browser.new_page(
                user_agent=iphone_user_agent,
                extra_http_headers={"Referer": "https://www.google.com", "X-Forwarded-For": ip}
            )
            # Очищаем cookies и кэш на стороне Playwright
            await page.context.clear_cookies()
            await page.goto(long_url)
            await page.wait_for_load_state('networkidle', timeout=60000)
            proxy_link = page.url
            await browser.close()

            logger.info(f"Токен для IP {ip} обновлен. Ссылка: {proxy_link}")
            return proxy_link
    except Exception as e:
        logger.error(f"Ошибка при регистрации токена для IP {ip}: {str(e)}")
        return None

# Функция для выдачи ссылок пользователю
async def get_actual_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_ip = get_public_ip()
    
    # Проверяем, нужно ли обновить токен для данного IP
    token_info = ip_token_cache.get(user_ip)
    current_time = time.time()

    if not token_info or current_time - token_info['last_update'] > TOKEN_LIFETIME:
        proxy_url = await register_token_for_ip(user_ip)
        if proxy_url:
            # Сохраняем новый токен и время обновления
            ip_token_cache[user_ip] = {'proxy_url': proxy_url, 'last_update': current_time}
            await update.message.reply_text(f"Токен обновлен для IP {user_ip}.\nТокен последний раз обновлен в {time.ctime(current_time)}")
        else:
            await update.message.reply_text(f"Не удалось обновить токен для IP {user_ip}. Пожалуйста, попробуйте позже.")
            return
    else:
        proxy_url = token_info['proxy_url']
        await update.message.reply_text(f"Токен актуален для IP {user_ip}. Последнее обновление: {time.ctime(token_info['last_update'])}")

    # Сайты для прокси
    sites = {
        "YouTube": "https://www.youtube.com",
        "Facebook": "https://www.facebook.com",
        "2IP": "https://www.2ip.ru",
        "TikTok": "https://www.tiktok.com",
        "Instagram": "https://www.instagram.com"
    }

    buttons = [
        [InlineKeyboardButton(f"Открыть {name}", web_app=WebAppInfo(url=f"https://easyproxy.tech/?__cpo={encode_url(url)}"))]
        for name, url in sites.items()
    ]

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Нажмите на одну из кнопок ниже, чтобы открыть сайт через наш прокси.", reply_markup=keyboard)

# Команда для запуска бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Получить актуальную ссылку")]], resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать! Нажмите кнопку ниже, чтобы получить актуальную ссылку на прокси.", reply_markup=keyboard)

# Главная функция запуска Telegram бота
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^Получить актуальную ссылку$"), get_actual_link))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
