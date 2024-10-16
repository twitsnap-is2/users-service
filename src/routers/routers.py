from fastapi import APIRouter, status, HTTPException, Query
from utils.engine import get_engine
from business_logic.users.users_schemas import UserAccountBase, UserCreationResponse, UserCompleteCreation, UserEmailResponse, UserInfoResponse, UserEmailExistsResponse, FollowResponse, FollowerAccountBase
from business_logic.users.users_service import UserAccountService
from middleware.error_middleware import ErrorResponse, ErrorResponseException
from loguru import logger
import os

router = APIRouter()
services = UserAccountService(get_engine())

@router.post("/users/temp", 
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

@router.put("/users/{user_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = {
        204: {"description": "User updated"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def update_user(user_id: str, data: UserCompleteCreation):
    try:
        if not services.update_useraccount(user_id, data):
            logger.error("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info("User updated")
        return

    except HTTPException as e:
        if e.status_code == 404:
            raise ErrorResponseException(
                type="https://httpstatuses.com/404",
                title="User not found",
                status=404,
                detail="User not found",
                instance="/users/{user_id}"
            )
    except ValueError as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=400, detail="Error updating user")
    except Exception as e:
        logger.error(f"Internal server error updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/users", 
    response_model = list[UserCreationResponse],
    status_code = status.HTTP_200_OK,
    responses = {
        200: {"description": "User list retrieved successfully"},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def get_users(filter: str | None = None):
    try:
        if filter:
            users = services.get_usernames_starting_with(filter)
        else:
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
    response_model = UserInfoResponse,
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
            raise ErrorResponseException(
                type="https://httpstatuses.com/404",
                title="User not found",
                status=404,
                detail="User not found",
                instance="/users/{user_id}"
            )
    except ErrorResponseException as e:
        raise e
    except ValueError as e:
        logger.error(f"Error retrieving user: {e}")
        raise HTTPException(status_code=400, detail="Error retrieving user")
    except Exception as e:
        logger.error(f"Internal server error retrieving user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/users/{username}/email",
    status_code = status.HTTP_200_OK,
    response_model = UserEmailResponse,
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
            return UserEmailResponse(email=email)
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
    
@router.get("/users/{email}/email/exists",
    status_code = status.HTTP_200_OK,
    response_model = UserEmailExistsResponse,
    responses = {
        200: {"description": "Email retrieved successfully"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def get_email_by_username(email: str):
    try:
        res = services.check_email_exists(email)
        return UserEmailExistsResponse(exists=res["exists"])
    except Exception as e:
        logger.error(f"Internal server error checking if email {email} exists: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")   

@router.get("/users/{user_id}/authorsUsernames/",
    status_code = status.HTTP_200_OK,
    response_model = list[UserCreationResponse],
    responses = {
        200: {"description": "User retrieved successfully"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def get_user_authors_info(user_id: str, authors: list[str] = Query(...)):
    try:
        users = services.get_user_authors_info(user_id, authors)
        if users:
            logger.info("Users retrieved successfully")
            return users
        else:
            logger.error("User not found")
            raise ErrorResponseException(
                type="https://httpstatuses.com/404",
                title="Users not found",
                status=404,
                detail="None of the users were found",
                instance="/users/{user_id}/authors_id/{authors_id}"
            )
    except ErrorResponseException as e:
        raise e
    except ValueError as e:
        logger.error(f"Error retrieving user: {e}")
        raise HTTPException(status_code=400, detail="Error retrieving user")
    except Exception as e:
        logger.error(f"Internal server error retrieving user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/users/search/", 
    response_model = list[UserCreationResponse],
    status_code = status.HTTP_200_OK,
    responses = {
        200: {"description": "User list retrieved successfully"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def search_users(username: str = Query(...)):
    try: 
        users = services.search_users(username)
        if users:
            logger.info("User list retrieved successfully")
            return users
        else:
            logger.error("User not found")
            raise ErrorResponseException(
                type="https://httpstatuses.com/404",
                title="Users not found",
                status=404,
                detail="None of the users were found",
                instance="/users/{user_id}/authors_id/{authors_id}"
            )
    except ErrorResponseException as e:
        raise e
    except ValueError as e:
        logger.error(f"Error retrieving user: {e}")
        raise HTTPException(status_code=400, detail="Error retrieving user")
    except Exception as e:
        logger.error(f"Internal server error retrieving user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/users/follow/{user_name}/", 
    response_model=FollowResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        200: {"description": "Follow action successfully"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def follow_user(follower_data: FollowerAccountBase, user_name: str):
    try: 
        follow_action = services.follow_user(follower_user_name=follower_data.user_name, followed_user_name=user_name)
        print(follow_action)
        if follow_action:
            logger.info("User followed successfully")
            return follow_action
        else:
            logger.error("User not found or already following")
            raise ErrorResponseException(
                type="https://httpstatuses.com/404",
                title="User not found or you are already following",
                status=404,
                detail="User not found or already following",
                instance="/users/{user_id}"
            )
    except ErrorResponseException as e:
        raise e
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.delete("/users/unfollow/{user_name}/", 
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        200: {"description": "Unfollow action successfully"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def unfollow_user(follower_data: FollowerAccountBase, user_name: str):
    try: 
        unfollow_action = services.unfollow_user(follower_user_name=follower_data.user_name, followed_user_name=user_name)
        if unfollow_action:
            logger.info("User unfollowed successfully")
        else:
            logger.error("User not found or not following")
            raise ErrorResponseException(
                type="https://httpstatuses.com/404",
                title="User not found or you are not following",
                status=404,
                detail="User not found or not following",
                instance="/users/unfollow/{user_name}"
            )
    except ErrorResponseException as e:
        raise e
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
@router.get("/users/followers/{user_name}/", 
    response_model=list[UserAccountBase],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Followers from user"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def followers(user_name: str):
    try: 
        user_followers = services.followers(user_name)
        if user_followers is None:
            logger.error("User not found")
            raise ErrorResponseException(
                type="https://httpstatuses.com/404",
                title="User not found",
                status=404,
                detail="User not found",
                instance="/users/{user_id}"
            )
        return user_followers
    except ErrorResponseException as e:
        raise e
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/users/following/{user_name}/", 
    response_model=list[UserAccountBase],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Following from user"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def followings(user_name: str):
    try: 
        user_followers = services.following(user_name)
        if user_followers is None:
            logger.error("User not found")
            raise ErrorResponseException(
                type="https://httpstatuses.com/404",
                title="User not found",
                status=404,
                detail="User not found",
                instance="/users/{user_id}"
            )
        return user_followers
    except ErrorResponseException as e:
        raise e
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
