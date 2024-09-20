from fastapi import FastAPI
from routers.routers import router
from middleware.error_middleware import ErrorHandlerMiddleware

app = FastAPI()

app.add_middleware(ErrorHandlerMiddleware)
app.include_router(router)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

