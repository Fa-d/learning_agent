from fastapi import FastAPI
from .api import learning

app = FastAPI()

app.include_router(learning.router)