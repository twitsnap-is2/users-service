from pydantic import BaseModel

class UserAccountBase(BaseModel):
    username: str
    mail: str
    password: str

# Inherits from base but contains id, needed for creation
class UserAccountCreate(UserAccountBase):
    id: str

# Inherits from base but contains id, needed for response
class UserAccount(UserAccountBase):
    id: str
 
    class Config:
        # orm_mode will tell the Pydantic model to read the data even if it is not a dict
        orm_mode = True