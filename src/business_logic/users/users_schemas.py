from pydantic import BaseModel, ConfigDict

class UserAccountBase(BaseModel):
    username: str
    mail: str
    password: str

# # Inherits from base but contains id, needed for creation
# class UserAccountCreate(UserAccountBase):
#     id: str

# Inherits from base but contains id, needed for response
class UserAccount(UserAccountBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
 
