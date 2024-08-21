from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Замените на конкретный домен в продакшене
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROXY_URL = 'https://www.easyproxy.tech/?__cpo=1'
BASE_PROXY_URL = 'https://www.easyproxy.tech'

@app.get("/get_initial_page")
async def get_initial_page(request: Request):
    client_ip = request.client.host
    async with httpx.AsyncClient() as client:
        response = await client.get(PROXY_URL, headers={'X-Forwarded-For': client_ip})
        return {"html": response.text}

@app.post("/submit_request")
async def submit_request(request: Request):
    client_ip = request.client.host
    data = await request.json()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_PROXY_URL}/requests",
            data=data,
            headers={'X-Forwarded-For': client_ip},
            allow_redirects=False
        )
        
        if response.status_code in [301, 302, 303, 307, 308]:
            return {"proxy_url": response.headers['Location']}
        else:
            return {"html": response.text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)