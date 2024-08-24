import time
import base64
import requests
import logging
import aiohttp
import json
from bs4 import BeautifulSoup
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

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
    return None  # Здесь должна быть логика для получения IP


# Функция для кодирования URL в Base64
def encode_url(url: str) -> str:
    return base64.b64encode(url.encode('utf-8')).decode('utf-8')


# Функция для получения времени +100 лет от текущего момента
def get_future_timestamp():
    future_date = datetime.now() + timedelta(days=365*100)
    return int(future_date.timestamp())

# Обновленная функция для регистрации токена
async def register_token_for_ip(ip: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            logger.info(f"Регистрация токена для IP {ip}")
            async with session.get(PROXY_URL) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')

            form = soup.find('form', id='request')
            csrf_token = form.find('input', {'name': 'csrf'})['value']

            # Создаем фиктивные данные Web App с временем +100 лет
            future_timestamp = get_future_timestamp()
            web_app_data = {
                'query_id': 'AAHGY0EIAAAAAMZjQQijDb7l',
                'user': json.dumps({
                    'id': 123456789,
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'username': 'johndoe',
                    'language_code': 'en',
                    'is_premium': False,
                    'allows_write_to_pm': True
                }),
                'auth_date': str(future_timestamp),
                'hash': 'dc7660343e2451b39da5fd291daf30d70e032780d73806ebb57fe0b9b4c229b7'
            }

            # Добавляем дополнительные параметры в data
            data = {
                'url': YOUTUBE_URL,
                'csrf': csrf_token,
                'tgWebAppData': json.dumps(web_app_data),
                'tgWebAppVersion': '7.2',
                'tgWebAppPlatform': 'tdesktop',
                'tgWebAppThemeParams': json.dumps({
                    'accent_text_color': '#6ab2f2',
                    'bg_color': '#17212b',
                    'button_color': '#5288c1',
                    'button_text_color': '#ffffff',
                    'destructive_text_color': '#ec3942',
                    'header_bg_color': '#17212b',
                    'hint_color': '#708499',
                    'link_color': '#6ab3f3',
                    'secondary_bg_color': '#232e3c',
                    'section_bg_color': '#17212b',
                    'section_header_text_color': '#6ab3f3',
                    'subtitle_text_color': '#708499',
                    'text_color': '#f5f5f5'
                })
            }

            async with session.post(f"{PROXY_URL}/requests", data=data, allow_redirects=False) as response:
                if response.status in [301, 302, 303, 307, 308]:
                    long_url = response.headers['Location']
                else:
                    long_url = str(response.url)

            # Возвращаем URL для регистрации
            logger.info(f"Ссылка на прокси для IP {ip}: {long_url}")
            return long_url
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
            await update.message.reply_text(f"Токен обновлен для IP {user_ip}. Ссылка: {proxy_url}")
            await update.message.reply_text("Пожалуйста, откройте ссылку в браузере для регистрации и закройте его после завершения.")
        else:
            await update.message.reply_text(f"Не удалось обновить токен для IP {user_ip}. Пожалуйста, попробуйте позже.")
            return
    else:
        proxy_url = token_info['proxy_url']
        last_update = datetime.fromtimestamp(token_info['last_update']).strftime('%Y-%m-%d %H:%M:%S')
        await update.message.reply_text(f"Токен актуален для IP {user_ip}. Последнее обновление: {last_update}")

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
            await update.message.reply_text(f"Токен обновлен для IP {user_ip}. Ссылка: {proxy_url}")
            await update.message.reply_text("Пожалуйста, откройте ссылку в браузере для регистрации и закройте его после завершения.")
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