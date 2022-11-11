import sqlite3
import typing as tp
import re

from linkr.internal.schemas import User, ShortUrl

# Connection should be a bit more managed than that for a prod service
DB_CON = sqlite3.connect("internal.db")

# Copy/pasted from python doc's example
def dict_factory(cursor, row):
    """Return query resul as dict"""
    col_names = [col[0] for col in cursor.description]
    return {key: value for key, value in zip(col_names, row)}

DB_CON.row_factory = dict_factory

# This should be ran outside of this module, during deployement.
def init_db():
    """Init db tables"""
    cur = DB_CON.cursor()
    cur.execute("""CREATE TABLE if not exists UsersData (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100),
        email VARCHAR(255),
        pwd_salt VARCHAR(512),
        pwd_hash VARCHAR(512)
    )""")
    cur.execute("""CREATE TABLE if not exists UrlData (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url_key VARCHAR(16),
        target VARCHAR(512),
        user_id INT,
        expiration DATETIME
    )""")

def convert_db_user_to_model(user: tp.Dict[str, tp.Any]):
    """Do the necessary name conversion to values from db and return a model"""
    user['uid'] = user.pop('id')
    return User(**user)

def get_user(
    name: tp.Optional[str] = None,
    email: tp.Optional[str] = None,
    uid: tp.Optional[int] = None
    ):
    """Get a specific user from db"""
    cur = DB_CON.cursor()
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
    cur.execute(f"SELECT * FROM UsersData WHERE {target_attr} = ?", (data,))
    values = cur.fetchone()
    return convert_db_user_to_model(values)

URL_KEY_PATTERN = re.compile(r"[A-z0-9]+\.[A-z0-9]{2,}-[A-z0-9]+")

# This should be paginated for a prod service
def get_users() -> tp.Tuple[User]:
    """Get all users from db"""
    cur = DB_CON.cursor()
    q = cur.execute(f"SELECT * FROM UsersData")
    return tuple(convert_db_user_to_model(values) for values in cur.fetchall())

def add_user(
    email: str,
    name: tp.Optional[str] = None,
    passwd: tp.Optional[str] = None,
) -> User:
    """Add a new user"""
    cur = DB_CON.cursor()
    cur.execute("SELECT * FROM UsersData WHERE email = ?", (email,))
    if cur.fetchone() is not None:
        raise ValueError("Email already registered")
    cur.execute(
        "INSERT INTO UsersData(email,name) VALUES(?, ?) RETURNING *",
        (email, name)
    )
    values = cur.fetchone()
    if values is None:
        raise RuntimeError("Fail to add new user")
    return convert_db_user_to_model(values)

def convert_db_url_to_model(data: tp.Dict[str, tp.Any]):
    """Do the necessary name conversion to values from db and return a model"""
    data['url_id'] = data.pop('id')
    return ShortUrl(**data)

def get_url_metadata(key: str) -> ShortUrl:
    """Get a specific url metadata"""
    cur = DB_CON.cursor()
    cur.execute("SELECT * FROM UrlData WHERE url_key = ?", (key,))
    values = cur.fetchone()
    if values is None:
        raise KeyError(f"No url for key '{key}'")
    return convert_db_url_to_model(values)

def get_available_key() -> tp.Optional[ShortUrl]:
    """Get an available key from db"""
    cur = DB_CON.cursor()
    cur.execute("SELECT * FROM UrlData WHERE expiration < NOW() OR target = ''")
    values = cur.fetchone()
    if values is not None:
        values = convert_db_url_to_model(values)
    return values

def 
