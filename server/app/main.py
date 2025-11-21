from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.gmail_test import router as gmail_test_router
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


app = FastAPI(title="InboxAI Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(gmail_test_router)

@app.get("/")
def root():
    return {"message": "Welcome to the InboxAI Server!"}