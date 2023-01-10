import datetime
import uuid
from math import floor
from typing import Dict, Union, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Cookie
from loguru import logger
from sqlalchemy.orm import Session
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, \
    HTTP_404_NOT_FOUND, HTTP_418_IM_A_TEAPOT

from api.schemas.responses import HTTP_400_RESPONSE, HTTP_404_RESPONSE
from database.engine import get_session
from database.models import User, Comment, Post, UserSession

from api.schemas.units import CreateUser, CreatePost, CreateComment, Login

authorization_router = APIRouter()


@authorization_router.post('/api/login', status_code=200,
                           name='Login', tags=['Api'])
def login(data: Login,
          session: Session = Depends(get_session)):
    data_dict = data.dict()
    user = session.query(User).filter(User.nickname == data_dict['login'],
                                      User.password == data_dict['password']).one_or_none()
    if user is None:
        user = session.query(User).filter(User.email == data_dict['login'],
                                          User.password == data_dict['password']).one_or_none()
    if user is None:
        raise HTTPException(status_code=400, detail='Invalid username/password.')
    session_id = session.query(UserSession).filter(UserSession.user_id == user.id).one_or_none()
    if session_id is None:
        session_id = str(uuid.uuid4())
        session_data = {
            "id": session_id,
            "user_id": str(user.id)
        }
        session.add(UserSession(**session_data))
        session.commit()
    content = {'message': 'Come to the dark side, we have cookies'}
    response = JSONResponse(content=content)
    response.set_cookie(key='session_id', value=session_id)
    return response


@authorization_router.post('/api/logout', status_code=200,
                             name='Logout', tags=['Api'])
def logout(session_id: UUID = Cookie(None),
           session: Session = Depends(get_session)):
    if session_id is None:
        raise HTTPException(status_code=400, detail='Already logged out!')
    user_session = session.query(UserSession).filter(UserSession.id == str(session_id)).one_or_none()
    if user_session is not None:
        session.delete(user_session)
        session.commit()
    else:
        raise HTTPException(status_code=400, detail='Already logged out!')
    content = {'message': 'You have left the dark side, you have lost your cookies'}
    response = JSONResponse(content=content)
    response.delete_cookie("session_id")
    return response
