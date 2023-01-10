import os

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config import get_settings
from api.schemas.error import ErrorResult
from api.router import api_router, authorization_router, secret_router
from loguru import logger
settings = get_settings()


def get_application() -> FastAPI:
    """AppFactory"""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version=settings.VERSION,
        description='Slonet'
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS or ['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    application.include_router(router=api_router, prefix=settings.API_PREFIX)
    application.include_router(router=authorization_router, prefix=settings.API_PREFIX)
    application.include_router(router=secret_router, prefix=settings.MAIN_PREFIX)

    @application.exception_handler(HTTPException)
    def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResult(code=exc.status_code,
                                message=exc.detail).dict(),
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        logger.error(exc)
        return JSONResponse(
            status_code=400,
            content=ErrorResult(code=400,
                                message='Validation Failed').dict(),
        )
    @application.exception_handler(Exception)
    async def validation_exception_handler(request, exc):
        logger.error(exc)
        return JSONResponse(
            status_code=503,
            content=ErrorResult(code=500,
                                message='Server Error').dict(),
        )

    return application


app = get_application()
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=int(os.environ.get("PORT", 80)))
