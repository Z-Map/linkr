import asyncio
import datetime
import re
import sqlite3
import typing as tp

import aiosqlite

from linkr.internal.schemas import User, ShortUrl

# Connection should be a bit more managed than that for a prod service
DB_NAME = "internal.db"

URL_KEY_PATTERN = re.compile(r"[A-z0-9]+\.[A-z0-9]{2,}-[A-z0-9]+")

def dict_factory(cursor, row):
    col_names = [col[0] for col in cursor.description]
    return {key: value for key, value in zip(col_names, row)}

class MasterDatabase():
    _db_instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._db_instance, class_):
            class_._db_instance = object.__new__(class_, *args, **kwargs)
        return class_._db_instance

    def __init__(self):
        self.db_name = DB_NAME
        self.con = None

    def __del__(self):
        asyncio.run(self.close())
        MasterDatabase._db_instance = None

    async def connection(self):
        """Returns current db connection"""
        if self.con is None:
            self.con = await aiosqlite.connect(self.db_name)
            self.con.row_factory = dict_factory
        return self.con

    async def close(self):
        """Close the connection"""
        if self.con is not None:
            await self.con.commit()
            await self.con.close()
            self.con.join(timeout=1)
            if self.con.is_alive():
                raise RuntimeError("Unable to close connection")
        self.con = None

    # User related method
    def convert_db_user_to_model(self, user: tp.Dict[str, tp.Any]):
        """Do the necessary name conversion to values from db and return a model"""
        user['uid'] = user.pop('id')
        return User(**user)

    async def get_user(self,
        name: tp.Optional[str] = None,
        email: tp.Optional[str] = None,
        uid: tp.Optional[int] = None
        ) -> User:
        """Get a specific user from db"""
        db = await self.connection()
        data = None
        target_attr = None
        error_msg = "No user name, email or id was provided"
        if name is not None:
            target_attr = "name"
            data = name
            error_msg = f"No user named '{name}'"
        elif email is not None:
            target_attr = "email"
            data = email
            error_msg = f"No user registered with email '{email}'"
        elif uid is not None:
            target_attr = "id"
            data = uid
            error_msg = f"No user with uid {uid}"
        else:
            raise ValueError(error_msg)
        async with db.execute(
            f"SELECT * FROM UsersData WHERE {target_attr} = ?", (data,)
        ) as cur:
            values = await cur.fetchone()
        if values is None:
            raise ValueError(error_msg)
        return self.convert_db_user_to_model(values)

    # This should be paginated for a prod service
    async def get_users(self) -> tp.Tuple[User]:
        """Get all users from db"""
        db = await self.connection()
        async with db.execute(f"SELECT * FROM UsersData") as cur:
            rows = await cur.fetchall()
        return tuple(self.convert_db_user_to_model(values) for values in rows)

    async def add_user(self,
        email: str,
        name: tp.Optional[str] = None,
        passwd: tp.Optional[str] = None,
    ) -> User:
        """Add a new user"""
        db = await self.connection()
        async with db.execute(
            "SELECT * FROM UsersData WHERE email = ?", (email,)) as cur:
            if await cur.fetchone():
                raise ValueError("Email already registered")
        async with db.execute(
            "INSERT INTO UsersData(email,name) VALUES(?, ?) RETURNING *",
            (email, name)) as cur:
            values = await cur.fetchone()
        await db.commit()
        if values is None:
            raise RuntimeError("Fail to add new user")
        return self.convert_db_user_to_model(values)

    # Url related method
    def convert_db_url_to_model(self, data: tp.Dict[str, tp.Any]):
        """Do the necessary name conversion to values from db and return a model"""
        data['url_id'] = data.pop('id')
        return ShortUrl(**data)

    async def get_url_metadata(self, key: str, domain: str) -> ShortUrl:
        """Get a specific url metadata"""
        db = await self.connection()
        async with db.execute(
            "SELECT * FROM UrlData WHERE url_key = ? AND url_domain = ?",
            (key, domain)
        ) as cur:
            values = await cur.fetchone()
            if values is None:
                raise KeyError(f"No url for key '{key}'")
        return self.convert_db_url_to_model(values)

    async def get_available_key(self) -> tp.Optional[ShortUrl]:
        """Get an available key from db"""
        db = await self.connection()
        async with db.execute(
            "SELECT * FROM UrlData WHERE expiration < DATETIME('now') OR target = ''"
        ) as cur:
            values = await cur.fetchone()
            if values is not None:
                values = self.convert_db_url_to_model(values)
        return values

    async def get_urls(self) -> tp.List[ShortUrl]:
        """Get a list of used url's metadata"""
        db = await self.connection()
        async with db.execute(
            "SELECT * FROM UrlData WHERE target != ''"
        ) as cur:
            res = [
                self.convert_db_url_to_model(values)
                for values in await cur.fetchall()
            ]
            print(res)
        return res

    async def get_new_url_index(self) -> int:
        """Return UrlData entries count"""
        db = await self.connection()
        async with db.execute("SELECT COUNT(*) FROM UrlData") as cur:
            result = await cur.fetchone()
        return result["COUNT(*)"]

    async def get_user_urls(self,
        uid: tp.Optional[int] = None,
        email: tp.Optional[str] = None
    ) -> tp.List[ShortUrl]:
        """Get a list of used url's metadata for a specific user"""
        db = await self.connection()
        if email is not None:
            try:
                usr = await self.get_user(email=email)
                uid = usr.uid
            except ValueError:
                return None
        async with db.execute(
            "SELECT * FROM UrlData WHERE user_id = ?", (uid,)
        ) as cur:
            return [
                self.convert_db_url_to_model(values)
                for values in await cur.fetchall()
            ]

    async def add_url(self,
        email: str,
        target: str,
        url_domain: str,
        url_key: str,

    ) -> User:
        """Add a new user"""
        db = await self.connection()
        try:
            usr = await self.get_user(email=email)
        except ValueError:
            usr = await self.add_user(email)
        async with db.execute(
            "INSERT INTO UrlData(url_domain, url_key, target, user_id,"
            "expiration) VALUES(?, ?, ?, ?, ?) RETURNING *", (
            url_domain, url_key, target, usr.uid,
            datetime.datetime.now() + datetime.timedelta(days=7)
        )) as cur:
            values = await cur.fetchone()
        await db.commit()
        if values is None:
            raise RuntimeError("Fail to add url")
        return self.convert_db_url_to_model(values)

# This should be ran outside of this module, during deployement.
def init_db(name: str):
    """Init db tables"""
    con = sqlite3.connect(name)
    cur = con.cursor()
    cur.executescript("""CREATE TABLE if not exists UsersData (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100),
        email VARCHAR(255),
        pwd_salt VARCHAR(512),
        pwd_hash VARCHAR(512)
    )""")
    cur.executescript("""CREATE TABLE if not exists UrlData (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url_domain VARCHAR(255),
        url_key VARCHAR(16),
        target VARCHAR(512),
        user_id INT,
        expiration DATETIME
    )""")
    cur.close()
    con.close()
