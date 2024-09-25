from pydantic import BaseModel, ConfigDict
from uuid import UUID

class UserAccountBase(BaseModel):
    username: str
    name: str
    email: str
    password: str
    birthdate: str
    location: str

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
    birthdate: str
    created_at: str
    profilepic: str | None = None

    model_config = ConfigDict(from_attributes=True)
