from pydantic import BaseModel, ConfigDict

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
    id: str
    username: str
    email: str
    name: str
    birthdate: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)