from pydantic import BaseModel

class EchoMsgBase(BaseModel):
    msg: str


class EchoMsgCreate(EchoMsgBase):
    id: int