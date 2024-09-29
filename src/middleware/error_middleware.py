from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

class ErrorResponse(BaseModel):
    """
    Class representing Error for a Response.

    Attributes:
        type: str (type of Error)
        title: str (Title of the Error)
        status: int (Status of Error) (400-404-500)
        detail: str (Deatil of the Error)
        instance: str (Instance of the Error)
    """

    type: str
    title: str
    status: int
    detail: str
    instance: str
    errors: Optional[Dict] = None

class ErrorResponseException(Exception):
    """
    Class representing Error for a Response.

    Attributes:
        type: str (type of Error)
        title: str (Title of the Error)
        status: int (Status of Error) (400-404-500)
        detail: str (Deatil of the Error)
        instance: str (Instance of the Error)
    """
    def __init__(self, type: str, title: str, status: int, detail: str, instance: str, errors: dict | None = None):
        self.type = type
        self.title = title
        self.status = status
        self.detail = detail
        self.instance = instance
        self.errors = errors

