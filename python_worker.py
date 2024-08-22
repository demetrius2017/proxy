import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROXY_URL = 'https://www.easyproxy.tech'
YOUTUBE_URL = 'https://www.youtube.com/'

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
        logger.error(f"Произошла ошибка: {str(e)}")
        return None

async def main():
    proxy_url = await get_proxy_url(YOUTUBE_URL)
    if proxy_url:
        logger.info(f"Итоговый прокси URL: {proxy_url}")
    else:
        logger.error("Не удалось получить прокси URL")

if __name__ == '__main__':
    asyncio.run(main())