from fastapi import APIRouter
from business_logic.schemas import EchoMsg

router = APIRouter()
services = Services(get_engine())

@router.get("/hello")
async def hello():
    return {"message": "Hello from the /hello endpoint"}

@router.get("/echo/{id}", response_model=EchoMsg)
async def read_echomsg(id: int):
    msg = services.get_echomsg(id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg




    

    

# Los routers son para los endopints. los diferenciamos en diferentes modulos. Por ejemplo si tenemos un endpoint para usuarios, lo ponemos en un modulo llamado users.py