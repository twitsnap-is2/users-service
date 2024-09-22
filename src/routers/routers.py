from fastapi import APIRouter, status, HTTPException
from utils.engine import get_engine
from business_logic.users.users_schemas import UserAccountBase
from business_logic.users.users_service import UserAccountService
from middleware.error_middleware import ErrorResponse

router = APIRouter()
services = UserAccountService(get_engine())

@router.post("/users", 
    response_model = str,
    status_code = status.HTTP_201_CREATED,
    responses = {
        201: {"description": "User created successfully"},
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def create_user(user: UserAccountBase):
    try:
        services.insert_useraccount(user)
        return "User created successfully"
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error inserting user")