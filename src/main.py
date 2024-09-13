from fastapi import fastapi
from .routers import router

app = FastAPI()

app.include_router(router)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

