from fastapi import FastAPI
from linkr.api.user import UserRouter
from linkr.api.url import UrlRouter

def define_linkr_api(app: FastAPI):
    """Define all route for the app"""
    api_app = FastAPI(title="Linkr API")

    # define all needed route
    api_app.include_router(UserRouter)
    api_app.include_router(UrlRouter)

    app.mount('/api', api_app)
    return api_app
