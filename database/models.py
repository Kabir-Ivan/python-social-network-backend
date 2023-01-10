import datetime
import enum
import logging
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, event, \
    select, update
from sqlalchemy.dialects.postgresql import UUID
from guid import GUID
from sqlalchemy.engine import Connection
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import ChoiceType

from database.base import Base
from database.engine import Session

logger = logging.getLogger('uvicorn')


class UnitType(str, enum.Enum):
    USER = 'USER'
    POST = 'POST'
    COMMENT = 'COMMENT'


class Comment(Base):
    __tablename__ = "comment"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    text = Column(String, nullable=True)
    creation_date = Column(DateTime(), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    parent_id = Column(UUID(as_uuid=True), ForeignKey("comment.id"), nullable=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.id"))

    def json(self):
        return {"text": self.text}

    def __str__(self):
        return f'{self.text}'

    def __repr__(self):
        return f'<Comment {self.header}>'


class Post(Base):
    __tablename__ = "post"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    header = Column(String, nullable=False)
    text = Column(String, nullable=False)
    creation_date = Column(DateTime(), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))

    comments: List["Comment"] = relationship(
        "Comment",
        backref=backref('Post', remote_side='Post.id'),
        uselist=True, cascade="all, delete"
    )

    def json(self):
        return {"header": self.header, "text": self.text}

    def __str__(self):
        return f'{self.text}'

    def __repr__(self):
        return f'<Post {self.header}>'


class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    nickname = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=True)
    about = Column(String, nullable=True)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    password = Column(String, nullable=True)
    join_date = Column(DateTime(), nullable=False)

    posts: List["Post"] = relationship(
        "Post",
        backref=backref('User', remote_side='User.id'),
        uselist=True, cascade="all, delete"
    )

    comments: List["Comment"] = relationship(
        "Comment",
        backref=backref('User', remote_side='User.id'),
        uselist=True, cascade="all, delete"
    )

    sessions: List["UserSession"] = relationship(
        "UserSession",
        backref=backref('User', remote_side='User.id'),
        uselist=True, cascade="all, delete"
    )

    def get_posts(self, num: int = 10 ** 9) -> Optional[List["Post"]]:
        return self.posts[:num]

    def json(self):
        return {"header": self.header, "text": self.text}

    def __str__(self):
        return f'{self.name} {self.surname}'

    def __repr__(self):
        return f'<User {self.name} {self.surname}>'


class UserSession(Base):
    __tablename__ = "session"
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True, nullable=False)
    id = Column(UUID(as_uuid=True), nullable=False)

    def json(self):
        return {"id": self.id, "user_id": self.user_id}

    def __str__(self):
        return f'{self.id}'

    def __repr__(self):
        return f'<UserSession {self.user_id} {self.id}>'


class File(Base):
    __tablename__ = "file"
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True, nullable=False)
    id = Column(UUID(as_uuid=True), nullable=False)
    path = Column(String, nullable=False)

    def json(self):
        return {"id": self.id, "user_id": self.user_id}

    def __str__(self):
        return f'{self.id}'

    def __repr__(self):
        return f'<File {self.user_id} {self.id}>'
