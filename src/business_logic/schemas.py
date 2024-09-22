from pydantic import BaseModel


class EchoMsgBase(BaseModel):
    msg: str

# Inherits from base but contains id, needed for creation
class EchoMsgCreate(EchoMsgBase):
    id: int

# Inherits from base but contains id, needed for response
class EchoMsg(EchoMsgBase):
    id: int
 
    class Config:
        # orm_mode will tell the Pydantic model to read the data even if it is not a dict
        orm_mode = True