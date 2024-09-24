from fastapi import APIRouter, status, HTTPException
from utils.engine import get_engine
from business_logic.users.users_schemas import UserAccountBase, UserCreationResponse
from business_logic.users.users_service import UserAccountService
from middleware.error_middleware import ErrorResponse
from loguru import logger


router = APIRouter()
services = UserAccountService(get_engine())

@router.post("/users", 
    response_model = UserCreationResponse,
    status_code = status.HTTP_201_CREATED,
    responses = {
        201: {"description": "User created successfully"},
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def create_user(user: UserAccountBase):
    try:
        user = services.insert_useraccount(user)
        if isinstance(user, UserCreationResponse):
            logger.info("User created successfully")
        return user
    except Exception as e:
        logger.error(f"Error inserting user: {e}")
        raise HTTPException(status_code=400, detail="Error inserting user")

@router.get("/users", 
    response_model = list[UserAccountBase],
    status_code = status.HTTP_200_OK,
    responses = {
        200: {"description": "User list retrieved successfully"},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def get_users():
    try:
        return services.get_useraccounts()
        logger.info("User list retrieved successfully")
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(status_code=400, detail="Error retrieving users")

