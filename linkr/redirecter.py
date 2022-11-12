import asyncio
import os
import typing as tp

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from linkr.internal.db import MasterDatabase, init_db, DB_NAME

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

@app.get("/{url_key}")
async def get_redirection(url_key: str):
    """Redirect client to the corresponding url"""
    db = MasterDatabase()
    try:
        url_data = await db.get_url_metadata(url_key, domain=TARGET_DOMAIN)
    except KeyError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err
    return RedirectResponse(url_data.target)

@app.get("/")
async def redirect_to_the_app(request: Request):
    """Redirect client to the main app"""
    return RedirectResponse(f"{request.url.scheme}://app.{TARGET_DOMAIN}")

