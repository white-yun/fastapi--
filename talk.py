import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import httpx
from datetime import datetime, timedelta

class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # 获取记录时间，并在其基础上加8个小时
        log_time = datetime.fromtimestamp(record.created) + timedelta(hours=8)
        # 格式化时间字符串
        if datefmt:
            return log_time.strftime(datefmt)
        else:
            return log_time.isoformat()

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# 设置自定义格式化器
for handler in logging.getLogger().handlers:
    handler.setFormatter(CustomFormatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

logger = logging.getLogger(__name__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        # logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        # logger.info(f"Response status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to log request body: {e}")

    return response

@app.post("/proxy-gallery")
async def proxy(request: Request):
    url = "https://qianfan.baidubce.com/v2/app/conversation"

    data = await request.json()
    logger.info(f"request===: {data}")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer bce-v3/ALTAK-nZyCv9CnD6iUfi1JoHASm/c7196afeb6ac314bf481f02ba421be877e312bf8',
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        result = response.json()
        logger.info(f"proxy-gallery response===: {result}")
        return response.json()

@app.post("/proxy-qianfan")
async def proxy_qianfan(request: Request):
    url = "https://qianfan.baidubce.com/v2/app/conversation/runs"
    data = await request.json()
    logger.info(f"request===: {data}")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer bce-v3/ALTAK-nZyCv9CnD6iUfi1JoHASm/c7196afeb6ac314bf481f02ba421be877e312bf8',
    }

    async def stream_response():
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=data, headers=headers) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
    logger.info(f"proxy-qianfan stream initiated")
    return StreamingResponse(stream_response(), media_type="application/json")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
