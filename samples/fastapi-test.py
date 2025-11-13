import uvicorn
from fastapi import FastAPI, Request

api = FastAPI()


@api.post("/api1")
async def handle_api2(data: dict):
    """
    シンプルにボディの型を定義するだけでも良い
    """
    print(f"data={data}")
    return data


@api.post("/api2")
async def handle_api(req: Request, data: dict | list[dict]) -> dict:
    """
    ``req: Request``を使うと、環境変数などの受け渡しができる(？)
    """
    req_body: bytes = await req.body()
    req_str: str = req_body.decode("utf-8")
    print(f"req_str={req_str}: {type(req_str)}")
    print(req.app.state)
    print(f"data={data}: {type(data)}")

    return {"req": req_str}


if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)
