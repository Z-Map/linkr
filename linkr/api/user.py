import typing as tp

from fastapi import APIRouter, Form

from linkr.internal.schemas import User
from linkr.internal import db

UserRouter = APIRouter()

@UserRouter.post("/user")
def create_user(
    email: str = Form(),
    username: str = Form(),
    password: tp.Optional[str] = Form()
) -> User:
    """Create an user"""
    return db.add_user(email, name=username, passwd=password)

@UserRouter.get("/user/by-id/{user_id}")
def get_user_by_id(
    user_id: int,
) -> User:
    """Get user based on user id"""
    return db.get_user(user_id=uid)

@UserRouter.get("/user/by-email/{email}")
def get_user_by_email(
    email: str,
) -> User:
    """Get user based on email"""
    return db.get_user(email=email)
