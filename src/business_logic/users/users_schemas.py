from pydantic import BaseModel, ConfigDict
from uuid import UUID

class UserAccountBase(BaseModel):
    username: str
    name: str
    email: str

# Inherits from base but contains id, needed for response
class UserAccount(UserAccountBase):
    id: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)
 
class UserCreationResponse(BaseModel):
    id: UUID
    username: str
    name: str
    email: str
    created_at: str
    profilePic: str | None = None

    model_config = ConfigDict(from_attributes=True)

class UserInfoResponse(UserCreationResponse):
    birthdate: str | None = None
    locationLat: float | None = None
    locationLong: float | None = None
    interests: str | None = None

    model_config = ConfigDict(from_attributes=True)

class UserCompleteCreation(BaseModel):
    supabase_id: str
    birthdate: str
    locationLat: float
    locationLong: float
    profilePic: str | None = None

class UserEmailResponse(BaseModel):
    email: str

class UserEmailExistsResponse(BaseModel):
    exists: bool

class FollowResponse(BaseModel):
    follower_id: UUID
    followed_id: UUID
    followed_at: str

class FollowerAccountBase(BaseModel):
    user_id: str
    
class UserEditProfile(BaseModel):
    name: str | None = None
    birthdate: str | None = None
    interests: str | None = None
    profilePic: str | None = None