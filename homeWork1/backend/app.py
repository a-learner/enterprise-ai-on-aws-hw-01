import os

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {
        "some_config": os.getenv("A_CONFIG", "I am default"),
        "secret_message": os.getenv("SECRET_MESSAGE", "Hello World"),
    }


@app.get("/health")
async def health():
    return {"status": "All is well! Be Happy!"}
