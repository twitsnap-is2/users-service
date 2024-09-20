from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except StarletteHTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "type": "about:blank",
                    "title": e.detail,
                    "status": e.status_code,
                    "detail": e.detail,
                    "instance": request.url.path,
                },
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "type": "about:blank",
                    "title": "Internal Server Error",
                    "status": 500,
                    "detail": str(e),
                    "instance": request.url.path,
                },
            )