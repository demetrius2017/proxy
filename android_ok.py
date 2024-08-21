import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram import Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = '7205474470:AAF5gNWm2mdtAJMbHa5Uj7LWg2y58sgI_NA'
PROXY_URL = 'https://www.easyproxy.tech'
YOUTUBE_URL = 'https://www.youtube.com/'

async def get_proxy_url(url: str = YOUTUBE_URL) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            # Шаг 1: Получаем начальную страницу
            async with session.get(PROXY_URL) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')

            # Шаг 2: Ищем форму и извлекаем CSRF-токен
            form = soup.find('form', id='request')
            csrf_token = form.find('input', {'name': 'csrf'})['value']

            # Шаг 3: Отправляем POST-запрос
            data = {
                'url': url,
                'csrf': csrf_token
            }
            async with session.post(f"{PROXY_URL}/requests", data=data, allow_redirects=False) as response:
                if response.status in [301, 302, 303, 307, 308]:
                    return response.headers['Location']
                else:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    meta_refresh = soup.find('meta', {'http-equiv': 'refresh'})
                    if meta_refresh:
                        content = meta_refresh['content']
                        return content.split('url=')[1]
                    else:
                        return str(response.url)

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    proxy_url = await get_proxy_url(YOUTUBE_URL)
    
    if proxy_url:
        await update.message.reply_text(
            "Welcome! Click the button below to open YouTube through our proxy.",
            reply_markup={
                "keyboard": [[{"text": "Open YouTube", "web_app": {"url": proxy_url}}]],
                "resize_keyboard": True
            }
        )
    else:
        await update.message.reply_text("Sorry, there was an error getting the proxy URL. Please try again later.")

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling(allowed_updates=Update.ALL_TYPES)