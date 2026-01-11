import os
import sys

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import courses, users, payments, admin, lessons
from database.base import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle"""
    await init_db()
    yield


app = FastAPI(
    title="DAROMATX Academy API",
    description="Kurs sotish platformasi API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(lessons.router, prefix="/api/lessons", tags=["Lessons"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/")
async def root():
    return {"message": "DAROMATX Academy API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
