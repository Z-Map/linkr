import asyncio
import typing as tp
import os

from fastapi import APIRouter, Form

from linkr.internal.schemas import User, ShortUrl
from linkr.internal.db import MasterDatabase
from linkr.internal.keygen import gen_key_from_index

UrlRouter = APIRouter()

TARGET_DOMAIN = os.environ.get("TARGET_DOMAIN", default="ln.kr")

@UrlRouter.get("/urls")
async def get_urls() -> tp.List[ShortUrl]:
    """Return a list of shortened url"""
    db = MasterDatabase()
    return await db.get_urls()

@UrlRouter.post("/url")
async def add_url(
    email: str = Form(),
    target_url: str = Form(),
    ) -> ShortUrl:
    """Return the new url"""
    db = MasterDatabase()
    available_url = await db.get_available_key()
    if available_url is None:
        idx = await db.get_new_url_index()
        url_key = gen_key_from_index(idx)
    else:
        url_key = available_url.url_key
    return await db.add_url(email, target_url, TARGET_DOMAIN, url_key)