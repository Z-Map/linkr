import asyncio
import os
import typing as tp

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from linkr.internal.db import MasterDatabase, init_db, DB_NAME
from linkr.api.main import define_linkr_api

app = FastAPI()

# This setting is here to alocate more than one domain name to the redirection
# engine so it is possible to continue scaling up in case we run out of id.
TARGET_DOMAIN = os.environ.get("TARGET_DOMAIN", default="ln.kr")

@app.on_event("startup")
def start_db():
    init_db(DB_NAME)

@app.on_event("shutdown")
async def close_db():
    db = MasterDatabase()
    await db.close()

define_linkr_api(app)