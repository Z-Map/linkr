import typing as tp
import datetime

from pydantic import BaseModel

class User(BaseModel):
    uid: int
    name: tp.Optional[str]
    email: str
    pwd_salt: tp.Optional[str]
    pwd_hash: tp.Optional[str]

class ShortUrl(BaseModel):
    url_id: int
    url_key: str
    target: str
    user_id: tp.Optional[int]
    expiration: datetime.datetime

