from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SETTLED = "settled"
    RETURNED = "returned"
    FAILED = "failed"


class PaymentSubmission(BaseModel):
    sender_account: str = Field(..., min_length=1, description="Sender's bank account number")
    receiver_account: str = Field(..., min_length=1, description="Receiver's bank account number")
    amount: float = Field(..., gt=0, description="Payment amount (must be positive)")
    memo: Optional[str] = Field(None, max_length=255, description="Optional payment memo")


class PaymentResponse(BaseModel):
    confirmation_id: str
    status: PaymentStatus
    created_at: datetime


class StatusResponse(BaseModel):
    confirmation_id: str
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
