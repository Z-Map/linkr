import typing as tp

from fastapi import APIRouter, Form

from linkr.internal.schemas import User, ShortUrl
from linkr.internal import db

UrlRouter = APIRouter()

@UrlRouter.get("/urls")
def get_urls() -> tp.List[ShortUrl]:
    """Return a list of shortened url"""
    return db.get_urls()