from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from routers.routers import router
from middleware.error_middleware import ErrorResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # It will only allow certain types of communication, excluding everything that involves credentials: Cookies, Authorization headers like those used with Bearer Tokens, etc.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handler for HTTPExceptions.

    Args:
        request: Request (Request object)
        exc: HTTPException (HTTPException object)

    Returns:
        JSONResponse: Response with the error.
    """
    if exc.status_code == 400:
        title = "Bad Request"
    elif exc.status_code == 404:
        title = "Snap Not Found"
    else:
        title = "Internal Server Error"

    error_response = ErrorResponse(
        type="about:blank",
        title=title,
        status=exc.status_code,
        detail=exc.detail,
        instance=str(request.url.path),
    )
    return JSONResponse(
        status_code=exc.status_code, content=error_response.model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    title = "Validation Error"
    status_code = 422
    details = exc.errors()
    detail = "JSON decode error"
    error_response = ErrorResponse(
        type="about:blank",
        title=title,
        status=status_code,
        detail=detail,
        instance=str(request.url.path),
    )
    return JSONResponse(
        status_code=status_code,
        content=error_response.dict(),
    )