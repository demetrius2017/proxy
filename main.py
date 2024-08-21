import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://147.45.238.24"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROXY_URL = 'https://www.easyproxy.tech/?__cpo=1'
BASE_PROXY_URL = 'https://www.easyproxy.tech'

@app.get("/get_initial_page")
async def get_initial_page(request: Request):
    client_ip = request.client.host
    logger.info(f"Получен запрос на начальную страницу от {client_ip}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(PROXY_URL, headers={'X-Forwarded-For': client_ip})
            response.raise_for_status()
            return {"html": response.text}
    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка HTTP при получении начальной страницы: {e}")
        raise HTTPException(status_code=e.response.status_code, detail="Ошибка при получении начальной страницы")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении начальной страницы: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.post("/submit_request")
async def submit_request(request: Request):
    client_ip = request.client.host
    logger.info(f"Получен запрос на отправку от {client_ip}")
    try:
        data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_PROXY_URL}/requests",
                data=data,
                headers={'X-Forwarded-For': client_ip},
                allow_redirects=False
            )
            response.raise_for_status()
            if response.status_code in [301, 302, 303, 307, 308]:
                return {"proxy_url": response.headers['Location']}
            else:
                return {"html": response.text}
    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка HTTP при отправке запроса: {e}")
        raise HTTPException(status_code=e.response.status_code, detail="Ошибка при отправке запроса")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке запроса: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

if __name__ == "__main__":
    import uvicorn
    logger.info("Запуск сервера на порту 8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)