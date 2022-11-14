import asyncio
import typing as tp

from fastapi import APIRouter, Form

from linkr.internal.schemas import User
from linkr.internal.db import MasterDatabase

UserRouter = APIRouter()

@UserRouter.post("/user")
async def create_user(
    email: str = Form(),
    username: str = Form(),
    password: tp.Optional[str] = Form()
) -> User:
    """Create an user"""
    db = MasterDatabase()
    return await db.add_user(email, name=username, passwd=password)

@UserRouter.get("/user/by-id/{user_id}")
async def get_user_by_id(
    user_id: int,
) -> User:
    """Get user based on user id"""
    db = MasterDatabase()
    return await db.get_user(user_id=uid)

@UserRouter.get("/user/by-email/{email}")
async def get_user_by_email(
    email: str,
) -> User:
    """Get user based on email"""
    db = MasterDatabase()
    return await db.get_user(email=email)
