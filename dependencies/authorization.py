from uuid import UUID
from fastapi import Cookie, Depends, HTTPException
from database.engine import get_session
from sqlalchemy.orm import Session
from database.models import User, Comment, Post, UserSession


def check_token(session_id: UUID = Cookie(None),
                      session: Session = Depends(get_session)):
    user_session = session.query(UserSession).filter(UserSession.id == str(session_id)).one_or_none()
    if user_session is None:
        raise HTTPException(status_code=403, detail='Forbidden!')