from fastapi import FastAPI
from routers.routers import router
from middleware.error_middleware import ErrorHandlerMiddleware
from services.services import Services
from utils import get_engine

app = FastAPI()
app.add_middleware(ErrorHandlerMiddleware)
app.include_router(router)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

