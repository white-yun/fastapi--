import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/proxy-gallery")
async def proxy(request: Request):
    url = "https://qianfan.baidubce.com/v2/app/conversation"
    data = await request.json()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer bce-v3/ALTAK-nZyCv9CnD6iUfi1JoHASm/c7196afeb6ac314bf481f02ba421be877e312bf8',
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        return response.json()

@app.post("/proxy-qianfan")
async def proxy_qianfan(request: Request):
    url = "https://qianfan.baidubce.com/v2/app/conversation/runs"
    data = await request.json()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer bce-v3/ALTAK-nZyCv9CnD6iUfi1JoHASm/c7196afeb6ac314bf481f02ba421be877e312bf8',
    }

    async def stream_response():
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=data, headers=headers) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(stream_response(), media_type="application/json")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
