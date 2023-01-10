import uuid
from datetime import datetime, timezone
from hashlib import sha256
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from dataclasses import dataclass

from pydantic import BaseModel, Field, validator, root_validator, EmailStr
from database.models import UnitType, Comment, Post, User
from fastapi import UploadFile, File


def convert_datetime(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec='seconds', ).replace('+00:00', 'Z')


import phonenumbers
from pydantic.validators import strict_str_validator


class PhoneNumber(str):
    @classmethod
    def __get_validators__(cls):
        yield strict_str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str):
        # Remove spaces
        v = v.strip().replace(' ', '')

        try:
            pn = phonenumbers.parse(v)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError('invalid phone number format')

        return cls(phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164))


class Config:
    use_enum_values = True
    arbitrary_types_allowed = True
    orm_mode = True
    allow_population_by_field_name = True


class BaseModel(BaseModel):
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True
        orm_mode = True
        allow_population_by_field_name = True


class BaseSchema(BaseModel):
    id: UUID = uuid.uuid4()

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True
        orm_mode = True
        allow_population_by_field_name = True


@dataclass
class UserSchema(BaseSchema):
    nickname: str
    name: str
    surname: Optional[str]
    about: Optional[str]
    join_date: datetime
    posts: List["PostSchema"]
    comments: List["CommentSchema"]
    phone: Optional[PhoneNumber]
    email: EmailStr
    password: str

    @validator("join_date")
    def date_conversion(cls, v):
        return convert_datetime(v)


class PostSchema(BaseSchema):
    header: str
    text: str
    creation_date: datetime = datetime.now()
    creator_id: UUID
    comments: List["CommentSchema"]

    @validator("creation_date")
    def date_conversion(cls, v):
        return convert_datetime(v)


class CommentSchema(BaseSchema):
    text: str
    creation_date: datetime
    creator_id: UUID
    parent_id: Optional[UUID]
    post_id: UUID

    @validator("creation_date")
    def date_conversion(cls, v):
        return convert_datetime(v)


class CreateUser(BaseModel):
    nickname: str
    name: str
    about: Optional[str]
    surname: Optional[str]
    phone: Optional[PhoneNumber]
    email: EmailStr
    password: str

    @validator("password")
    def hashing(cls, v):
        return sha256(v.encode('utf-8')).hexdigest()


class CreatePost(BaseModel):
    header: str
    text: str


class CreateComment(BaseModel):
    text: str
    creation_date: datetime
    parent_id: Optional[UUID]
    post_id: UUID


class Login(BaseModel):
    login: str
    password: str

    @validator("password")
    def hashing(cls, v):
        return sha256(v.encode('utf-8')).hexdigest()


class UserResponseSchema(BaseModel):
    nickname: str
    name: str
    about: str
    surname: Optional[str]
    join_date: Optional[datetime]


class PostsResponseSchema(BaseModel):
    posts: List["PostSchema"] = None


class CommentsResponseSchema(BaseModel):
    comments: List["CommentSchema"] = None


UserSchema.update_forward_refs()
PostSchema.update_forward_refs()
CommentSchema.update_forward_refs()
