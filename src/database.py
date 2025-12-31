import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://payments:payments@localhost:5432/payments"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.

    Usage in your routes:
        from fastapi import Depends
        from .database import get_db
        from sqlalchemy.orm import Session

        @router.post("/")
        def create_payment(db: Session = Depends(get_db)):
            # use db to query/insert
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Create all tables in the database.

    Call this on app startup after defining your models.
    Your models should inherit from Base:

        from .database import Base

        class Payment(Base):
            __tablename__ = "payments"
            # TODO: Define your columns here
    """
    Base.metadata.create_all(bind=engine)
