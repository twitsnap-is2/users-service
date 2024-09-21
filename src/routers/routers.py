from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
async def hello():
    return {"message": "Hello from the /hello endpoint"}

# Los routers son para los endopints. los diferenciamos en diferentes modulos. Por ejemplo si tenemos un endpoint para usuarios, lo ponemos en un modulo llamado users.py