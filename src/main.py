from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from routers.routers import router
from middleware.error_middleware import ErrorResponse, ErrorResponseException
from fastapi.middleware.cors import CORSMiddleware
import os
import requests


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # It will only allow certain types of communication, excluding everything that involves credentials: Cookies, Authorization headers like those used with Bearer Tokens, etc.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

@app.middleware("http")
async def useApiKey(request: Request, call_next):
    # if the request is /docs/* or /openapi.json or the ENV is test, the middleware will not be executed

    if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json") or os.getenv("ENV") == "test":
        return await call_next(request)

    try:
        bearer = request.headers.get("Authorization")
        if not bearer:
            raise ErrorResponseException(
                type="https://httpstatuses.com/503",
                status=503,
                title="Service Unavailable",
                detail="API key is required",
                instance=str(request.url.path),
            )
        token = bearer.split(" ")[1]
        if not token:
            raise ErrorResponseException(
                type="https://httpstatuses.com/503",
                status=503,
                title="Service Unavailable",
                detail="API key is required",
                instance=str(request.url.path),
            )
            

        # make a POST request to ENV API_SERVICE_MANAGER providing de token as the body

        res = requests.post(
            f"{os.getenv('API_SERVICE_MANAGER')}/manager/validate",
            headers={"Authorization": f"Bearer {os.getenv('API_KEY')}"},
            json={"APIKey": token},
        )

        if res.status_code != 200:
            raise ErrorResponseException(
                type="https://httpstatuses.com/503",
                status=503,
                title="Service Unavailable",
                detail="API key is invalid",
                instance=str(request.url.path),
            )

         
        return await call_next(request)
    except ErrorResponseException as e:
        error_response = ErrorResponse(
            type="about:blank",
            title=e.title,
            status=e.status,
            detail=e.detail,
            instance=str(request.url.path),
        )
        return JSONResponse(
            status_code=e.status, content=error_response.model_dump()
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
        content=error_response.model_dump(),
    )

@app.exception_handler(ErrorResponseException)
async def validation_exception_handler(request: Request, exc: ErrorResponseException):

    return JSONResponse(
        status_code=exc.status,
        content={
            "type": exc.type,
            "title": exc.title,
            "status": exc.status,
            "detail": exc.detail,
            "instance": str(request.url.path),
            "errors": exc.errors,
        },
    )