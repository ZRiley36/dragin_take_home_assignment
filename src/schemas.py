"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    """Request schema for creating a new payment."""
    sender_account: str = Field(..., description="Sender's account number")
    receiver_account: str = Field(..., description="Receiver's account number")
    amount: float = Field(..., gt=0, description="Payment amount (must be positive)")
    memo: Optional[str] = Field(None, description="Optional payment memo")


class PaymentResponse(BaseModel):
    """Response schema for payment endpoints."""
    id: str = Field(..., description="Internal payment ID")
    confirmation_id: Optional[str] = Field(None, description="Gateway's confirmation ID")
    sender_account: str
    receiver_account: str
    amount: float
    memo: Optional[str]
    status: str = Field(..., description="Payment status: pending, settled, returned, or failed")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentUpdate(BaseModel):
    """Internal schema for status updates from gateway."""
    confirmation_id: str
    status: str
    updated_at: datetime

