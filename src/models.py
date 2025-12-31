"""
Database models for the payment tracking system.
"""
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.sql import func

from .database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True)  # UUID for internal tracking
    confirmation_id = Column(String, nullable=True)  # Gateway's confirmation ID
    sender_account = Column(String, nullable=False)
    receiver_account = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    memo = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")  # pending, settled, returned, failed
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
