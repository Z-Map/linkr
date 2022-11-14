import asyncio
import os
import os.path as osp

import aiosqlite
import pytest
import pytest_asyncio

from linkr.internal.schemas import User
from linkr.internal import db

pytestmark = pytest.mark.asyncio

db.DB_NAME = osp.join(osp.dirname(__file__), "test.db")

TEST_USER = User(
    uid=1,
    email="user@test.com",
    name="Marvin"
)

@pytest.fixture(scope="session")
def event_loop():
    if osp.isfile(db.DB_NAME):
        os.unlink(db.DB_NAME)
    db.init_db(db.DB_NAME)
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

async def reset_user_table(dbo):
    con = await dbo.connection()
    await con.execute("DELETE FROM UsersData")
    await con.execute("DELETE FROM sqlite_sequence WHERE name='UsersData'")
    await con.commit()

@pytest_asyncio.fixture(scope="module")
async def dbo():
    db_object = db.MasterDatabase()
    con = await db_object.connection()
    await reset_user_table(db_object)
    yield db_object
    await db_object.close()

async def test_get_users_empty(dbo):
    users = await dbo.get_users()
    assert users == tuple()

async def test_add_users(dbo):
    usr = await dbo.add_user(TEST_USER.email, name=TEST_USER.name)
    assert usr == TEST_USER

async def test_get_users(dbo):
    assert await dbo.get_users() == (TEST_USER,)

async def test_get_user(dbo):
    assert await dbo.get_user(email=TEST_USER.email) == TEST_USER

async def test_get_user(dbo):
    assert await dbo.get_user(name=TEST_USER.name) == TEST_USER

async def test_get_available(dbo):
    assert await dbo.get_available_key() is None

async def test_add_url(dbo):
    assert await dbo.add_url(TEST_USER.email, "test.url", "ln.kr", "G8j")

async def test_get_user_url(dbo):
    urls = await dbo.get_user_urls(email=TEST_USER.email)
    assert urls

async def test_get_user_url(dbo):
    assert await dbo.get_new_url_index() == 1