from fastapi import APIRouter, status, HTTPException
from utils.engine import get_engine
from business_logic.users.users_schemas import UserAccountBase, UserCreationResponse
from business_logic.users.users_service import UserAccountService
from middleware.error_middleware import ErrorResponse, ErrorResponseException
from loguru import logger
import os

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
    logger.debug(user.model_dump_json())
    try:
        user = services.insert_useraccount(user)
        if isinstance(user, UserCreationResponse):
            logger.info("User created successfully")
        return user
    except Exception as e:
        error_message = str(e)
        if "duplicate key value violates unique constraint \"users_username_key\"" in error_message:
            raise ErrorResponseException(
                type="https://httpstatuses.com/400",
                title="Bad Request",
                status=400,
                detail="User already exists",
                instance=os.getenv("API_INSTANCE"),
                errors={"username": "User already exists"}
            )
        if "duplicate key value violates unique constraint \"users_email_key\"" in error_message:
            raise ErrorResponseException(
                type="https://httpstatuses.com/400",
                title="Bad Request",
                status=400,
                detail="Email already exists",
                instance=os.getenv("API_INSTANCE"),
                errors={"email": "Email already exists"}
            )
        logger.error(f"Error inserting user: {e}")
        raise HTTPException(status_code=400, detail="Error inserting user")

@router.get("/users", 
    response_model = list[UserCreationResponse],
    status_code = status.HTTP_200_OK,
    responses = {
        200: {"description": "User list retrieved successfully"},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def get_users():
    try:
        users = services.get_useraccounts()
        logger.info("User list retrieved successfully")
        return users
    except ValueError as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(status_code=400, detail="Error retrieving users")
    except Exception as e:
        logger.error(f"Internal server error retrieving users: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/users/{user_id}",
    response_model = UserCreationResponse,
    status_code = status.HTTP_200_OK,
    responses = {
        200: {"description": "User retrieved successfully"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def get_user(user_id: str):
    try:
        user = services.get_useraccount(user_id)
        if user:
            logger.info("User retrieved successfully")
            return user
        else:
            logger.error("User not found")
            raise HTTPException(status_code=404, detail="User not found")
    except ValueError as e:
        logger.error(f"Error retrieving user: {e}")
        raise HTTPException(status_code=400, detail="Error retrieving user")
    except Exception as e:
        logger.error(f"Internal server error retrieving user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/users/{username}/email",
    status_code = status.HTTP_200_OK,
    responses = {
        200: {"description": "Email retrieved successfully"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def get_email_by_username(username: str):
    try:
        email = services.get_email_by_username(username)
        if email:
            logger.info("Email retrieved successfully")
            return {"email": email}
        else:
            logger.error("User not found")
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException as e:
        if e.status_code == 404:
            raise ErrorResponseException(
                type="https://httpstatuses.com/404",
                title="User not found",
                status=404,
                detail="User not found",
                instance="/users/{username}/email",
                errors={"email": "email not found"}
            )
    except ValueError as e:
        logger.error(f"Error retrieving email: {e}")
        raise HTTPException(status_code=400, detail="Error retrieving email")
    except Exception as e:
        logger.error(f"Internal server error retrieving email: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")   
