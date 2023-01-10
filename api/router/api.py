import datetime
import uuid
from math import floor
from typing import Dict, Union, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Cookie, UploadFile, File
from loguru import logger
from sqlalchemy.orm import Session
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, \
    HTTP_404_NOT_FOUND, HTTP_418_IM_A_TEAPOT, HTTP_201_CREATED, \
    HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED
from api.schemas.responses import HTTP_400_RESPONSE, HTTP_404_RESPONSE
from database.engine import get_session
from database.models import User, Comment, Post, UserSession
from database.filestorage import upload_one, upload_many

from api.schemas.units import CreateUser, CreatePost, CreateComment, Login, \
    CommentsResponseSchema, PostsResponseSchema, PostSchema, UserResponseSchema

api_router = APIRouter()


@api_router.post('/create_user', status_code=HTTP_201_CREATED,
                 name='Create user', tags=['Api'])
def create_user(user: CreateUser,
                session: Session = Depends(get_session)):
    user_data = user.dict()
    user_data['join_date'] = datetime.datetime.now()
    user_data['id'] = uuid.uuid4()
    same_username_user = session.query(User).filter(User.nickname == user_data['nickname']).one_or_none()
    same_email_user = session.query(User).filter(User.email == user_data['email']).one_or_none()
    same_phone_user = session.query(User).filter(User.phone == user_data['phone']).one_or_none()
    if same_username_user is not None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Username already in use!')
    elif same_email_user is not None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Email already in use!')
    elif same_phone_user is not None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Phone already in use!')
    # filename = str(uuid.uuid4())
    # upload_one(avatar, filename)
    session.add(User(**user_data))
    session.commit()
    content = {"id": str(user_data['id'])}
    return JSONResponse(content=content)



@api_router.post('/create_post', status_code=HTTP_201_CREATED,
                 name='Create post', tags=['Api'])
def create_post(post: CreatePost,
                session: Session = Depends(get_session),
                session_id: UUID = Cookie(None)):
    user_session = session.query(UserSession).filter(UserSession.id == str(session_id)).one_or_none()
    if user_session is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Unauthorized!')
    post_data = post.dict()
    post_data['id'] = uuid.uuid4()
    post_data['creation_date'] = datetime.datetime.now()
    post_data['creator_id'] = user_session.user_id
    creator_user = session.query(User).filter(User.id == post_data['creator_id']).one_or_none()
    if creator_user is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Wrong creator id!')
    session.add(Post(**post_data))
    session.commit()
    content = {"id": str(post_data['id'])}
    return JSONResponse(content=content)


@api_router.post('/create_comment', status_code=HTTP_201_CREATED,
                 name='Create comment', tags=['Api'])
def create_comment(comment: CreateComment,
                   session: Session = Depends(get_session),
                   session_id: UUID = Cookie(None)):
    user_session = session.query(UserSession).filter(UserSession.id == str(session_id)).one_or_none()
    if user_session is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Unauthorized!')
    comment_data = comment.dict()
    comment_data['id'] = uuid.uuid4()
    comment_data['creation_date'] = datetime.datetime.now()
    comment_data['creator_id'] = user_session.user_id
    if comment_data['parent_id'] is not None:
        parent = session.query(Comment).filter(Comment.id == comment_data['parent_id']).one_or_none()
        if parent is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Wrong parent id!')
    creator_user = session.query(User).filter(User.id == comment_data['creator_id']).one_or_none()
    if creator_user is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Wrong creator id!')
    session.add(Comment(**comment_data))
    session.commit()
    content = {"id": str(comment_data['id'])}
    return JSONResponse(content=content)


@api_router.delete('/delete_user', status_code=HTTP_200_OK,
                   name='Delete user', tags=['Api'])
def delete_user(session_id: UUID = Cookie(None),
                session: Session = Depends(get_session)):
    user_session = session.query(UserSession).filter(UserSession.id == str(session_id)).one_or_none()
    if user_session is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Unauthorized!')
    user = session.query(User).filter(User.id == str(user_session.user_id)).one_or_none()
    session.delete(user)
    session.commit()
    return Response(status_code=HTTP_200_OK)


@api_router.delete('/delete_post', status_code=HTTP_200_OK,
                   name='Delete post', tags=['Api'])
def delete_post(post_id: UUID,
                session: Session = Depends(get_session),
                session_id: UUID = Cookie(None)):
    user_session = session.query(UserSession).filter(UserSession.id == str(session_id)).one_or_none()
    if user_session is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Unauthorized!')
    post = session.query(Post).filter(Post.id == str(post_id)).one_or_none()
    if post is not None:
        session.delete(post)
        session.commit()
    else:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Post id does not exist!')
    return Response(status_code=HTTP_200_OK)


@api_router.delete('/delete_comment', status_code=HTTP_200_OK,
                   name='Delete comment', tags=['Api'])
def delete_comment(comment_id: UUID,
                   session: Session = Depends(get_session),
                   session_id: UUID = Cookie(None)):
    user_session = session.query(UserSession).filter(UserSession.id == str(session_id)).one_or_none()
    if user_session is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Unauthorized!')
    comment = session.query(Comment).filter(Comment.id == str(comment_id)).one_or_none()
    if comment is not None:
        session.delete(comment)
        session.commit()
    else:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Comment id does not exist!')
    return Response(status_code=HTTP_200_OK)


@api_router.get('/get_comments', status_code=HTTP_200_OK,
                name='Get comments', tags=['Api'], response_model=CommentsResponseSchema)
def get_comments(post_id: UUID,
                 session: Session = Depends(get_session),
                 session_id: UUID = Cookie(None)):
    user_session = session.query(UserSession).filter(UserSession.id == str(session_id)).one_or_none()
    if user_session is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Unauthorized!')
    comments = session.query(Comment).filter(Comment.post_id == str(post_id)).all()
    if comments is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Comments not found!')
    return CommentsResponseSchema(comments=comments)


@api_router.get('/get_posts', status_code=HTTP_200_OK,
                name='Get posts', tags=['Api'], response_model=PostsResponseSchema)
def get_posts(user_id: UUID,
              session: Session = Depends(get_session),
              session_id: UUID = Cookie(None)):
    user_session = session.query(UserSession).filter(UserSession.id == str(session_id)).one_or_none()
    if user_session is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Unauthorized!')
    posts = session.query(Post).filter(Post.creator_id == str(user_id)).all()
    if posts is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Posts not found!')
    posts_list = []
    for post in posts:
        post_data = post.__dict__
        post_data['comments'] = get_comments(post_data['id'], session, session_id).comments
        posts_list.append(PostSchema(**post_data))
    return PostsResponseSchema(posts=posts)


@api_router.get('/get_user', status_code=HTTP_200_OK,
                name='Get user', tags=['Api'], response_model=UserResponseSchema)
def get_posts(nickname: str,
              session: Session = Depends(get_session),
              session_id: UUID = Cookie(None)):
    user_session = session.query(UserSession).filter(UserSession.id == str(session_id)).one_or_none()
    if user_session is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Unauthorized!')
    user = session.query(User).filter(User.nickname == nickname).one_or_none()
    if user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found!')
    return UserResponseSchema(**user.__dict__)
