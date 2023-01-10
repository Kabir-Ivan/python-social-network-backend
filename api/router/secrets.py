from fastapi import APIRouter, HTTPException, UploadFile, File
from starlette.responses import Response, JSONResponse
from typing import Dict

secret_router = APIRouter()


@secret_router.get('/', name='Test', tags=['Test'])
def get_test() -> Dict[str, str]:
    content = {"message": "Success?"}
    response = JSONResponse(content=content)
    return response


@secret_router.get('/brew_coffee', name='Test', tags=['Test'])
def get_test() -> Dict[str, str]:
    raise HTTPException(status_code=418, detail='I am a teapot.')
