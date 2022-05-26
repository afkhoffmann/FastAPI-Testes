import uvicorn
from fastapi import FastAPI


app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


def start():
    uvicorn.run("api_requests.api:app", host="0.0.0.0", port=8001, reload=True)


if __name__ == "__main__":
    start()
