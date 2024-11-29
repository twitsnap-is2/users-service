from fastapi import APIRouter, status, HTTPException, Query, Depends
from utils.engine import get_engine
from business_logic.users.users_schemas import UserAccountBase, UserCreationResponse, UserCompleteCreation, UserEmailResponse, UserInfoResponse, UserEmailExistsResponse, FollowResponse, FollowerAccountBase, UserEditProfile
from business_logic.users.users_service import UserAccountService
from middleware.error_middleware import ErrorResponse, ErrorResponseException
from loguru import logger
import os
from fastapi.security import HTTPBearer

router = APIRouter()
services = UserAccountService(get_engine())
security_scheme = HTTPBearer()

@router.post("/users/temp", 
    response_model = UserCreationResponse,
    status_code = status.HTTP_201_CREATED,
    responses = {
        201: {"description": "User created successfully"},
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def create_user(user: UserAccountBase, token: str = Depends(security_scheme)):
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
async def update_user(user_id: str, data: UserCompleteCreation, token: str = Depends(security_scheme)):
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
async def get_users(filter: str | None = None, token: str = Depends(security_scheme)):
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
async def get_user(user_id: str, token: str = Depends(security_scheme)):
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
async def get_email_by_username(username: str, token: str = Depends(security_scheme)):
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
async def check_email_exists(email: str, token: str = Depends(security_scheme)):
    try:
        res = services.check_email_exists(email)
        return UserEmailExistsResponse(exists=res["exists"])
    except Exception as e:
        logger.error(f"Internal server error checking if email {email} exists: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")   

@router.get("/users/{user_id}/authorsUsernames/",
    status_code = status.HTTP_200_OK,
    response_model = list[UserInfoResponse],
    responses = {
        200: {"description": "User retrieved successfully"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def get_user_authors_info(user_id: str, authors: list[str] = Query(...), token: str = Depends(security_scheme)):
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
    
@router.get("/users/{user_id}/authorsIds/",
    status_code = status.HTTP_200_OK,
    response_model = list[UserInfoResponse],
    responses = {
        200: {"description": "User retrieved successfully"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },)
async def get_user_authors_info_id(user_id: str, authors: list[str] = Query(...), token: str = Depends(security_scheme)):
    try:
        users = services.get_user_authors_info_id(user_id, authors)
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
async def search_users(username: str = Query(...), token: str = Depends(security_scheme)):
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
                instance="/users/search/"
            )
    except ErrorResponseException as e:
        raise e
    except ValueError as e:
        logger.error(f"Error retrieving user: {e}")
        raise HTTPException(status_code=400, detail="Error retrieving user")
    except Exception as e:
        logger.error(f"Internal server error retrieving user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/users/follow/{user_id}/", 
    response_model=FollowResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        200: {"description": "Follow action successfully"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def follow_user(follower_data: FollowerAccountBase, user_id: str, token: str = Depends(security_scheme)):
    try: 
        follow_action = services.follow_user(follower_user_id=follower_data.user_id, followed_user_id=user_id)
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
                instance="/users/follow/{user_id}/"
            )
    except ErrorResponseException as e:
        raise e
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.delete("/users/unfollow/{user_id}/", 
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Unfollow action successfully"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def unfollow_user(follower_data: FollowerAccountBase, user_id: str, token: str = Depends(security_scheme)):
    try: 
        unfollow_action = services.unfollow_user(follower_user_id=follower_data.user_id, followed_user_id=user_id)
        if unfollow_action:
            logger.info("User unfollowed successfully")
        else:
            logger.error("User not found or not following")
            raise ErrorResponseException(
                type="https://httpstatuses.com/404",
                title="User not found or you are not following",
                status=404,
                detail="User not found or not following",
                instance="/users/unfollow/{user_id}"
            )
    except ErrorResponseException as e:
        raise e
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
@router.get("/users/followers/{user_id}/", 
    response_model=list[UserCreationResponse],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Followers from user"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_followers(user_id: str, token: str = Depends(security_scheme)):
    try: 
        user_followers = services.get_followers(user_id)
        if user_followers is None:
            logger.error("User not found")
            raise ErrorResponseException(
                type="https://httpstatuses.com/404",
                title="User not found",
                status=404,
                detail="User not found",
                instance="/users/followers/{user_id}/"
            )
        return user_followers
    except ErrorResponseException as e:
        raise e
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/users/following/{user_id}/", 
    response_model=list[UserCreationResponse],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Following from user"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_following(user_id: str, token: str = Depends(security_scheme)):
    try: 
        user_followers = services.get_following(user_id)
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

@router.put("/users/edit/{user_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    responses = {
        204: {"description": "User updated"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def edit_user_profile(user_id: str, data: UserEditProfile, token: str = Depends(security_scheme)):
    try:
        if not services.update_user_profile(user_id, data):
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
    
@router.get("/users/near/{user_id}/", 
    response_model = list[UserCreationResponse],
    status_code = status.HTTP_200_OK,
    responses = {
        200: {"description": "User list retrieved successfully"},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_near_users(user_id: str):
    try:
        users = services.get_near_users(user_id)
        logger.info("User list retrieved successfully")
        return users
    except ValueError as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(status_code=400, detail="Error retrieving users")
    except Exception as e:
        logger.error(f"Internal server error retrieving users: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/users/common-interests/{user_id}/", 
    response_model = list[UserCreationResponse],
    status_code = status.HTTP_200_OK,
    responses = {
        200: {"description": "User list retrieved successfully"},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_users_with_common_interests(user_id: str):
    try:
        users = services.get_users_with_common_interests(user_id)
        logger.info("User list retrieved successfully")
        return users
    except ValueError as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(status_code=400, detail="Error retrieving users")
    except Exception as e:
        logger.error(f"Internal server error retrieving users: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
@router.get("/users/grouped-by-country/",
    response_model = list[UserCreationResponse],
    status_code = status.HTTP_200_OK,
    responses = {
        200: {"description": "User list retrieved successfully"},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)

async def get_users_grouped_by_country():
    try:
        users = services.get_users_grouped_by_country()
        logger.info("User list retrieved successfully")
        return users
    except ValueError as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(status_code=400, detail="Error retrieving users")
    except Exception as e:
        logger.error(f"Internal server error retrieving users: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

