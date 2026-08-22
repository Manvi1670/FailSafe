# ============================================================
# main.py — FastAPI app entry point (all routers)
# ============================================================
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import auth_router, predict, students, dashboard, interventions

app = FastAPI(
    title="FAILSAFE API",
    description="Student failure prediction and intervention system",
    version="1.0.0"
)

allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]
client_url = os.getenv("CLIENT_URL")
if client_url:
    allowed_origins.append(client_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(predict.router)
app.include_router(students.router)
app.include_router(dashboard.router)
app.include_router(interventions.router)


@app.get("/")
def root():
    return {
        "message": "FAILSAFE API is running",
        "version": "1.0.0",
        "docs"   : "http://127.0.0.1:8000/docs"
    }