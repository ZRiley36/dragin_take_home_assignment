from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import init_db

# TODO: Import your routers here
# from .routes import payments


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create database tables
    init_db()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Payment Tracking Service",
    description="Your payment tracking service - implement the endpoints!",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# TODO: Include your payment routes
# app.include_router(payments.router, prefix="/payments", tags=["payments"])
