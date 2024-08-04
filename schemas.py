# schemas.py
from pydantic import BaseModel

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    sender: str

    class Config:
        orm_mode = True
