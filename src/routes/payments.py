"""
Payment Routes

Required endpoints:
1. POST /payments - Submit a new payment
2. GET /payments/{payment_id} - Get payment status
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import httpx

from ..database import get_db
from ..models import Payment
from ..schemas import PaymentCreate, PaymentResponse
from ..gateway_client import gateway_client

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    """
    Submit a new payment.
    
    - Accept payment details from the user
    - Store the payment in your database
    - Forward the payment to the remote gateway
    - Return the payment with its initial status
    """
    # Generate UUID for internal payment ID
    payment_id = str(uuid.uuid4())
    
    # Create payment record in database with initial status "pending"
    db_payment = Payment(
        id=payment_id,
        sender_account=payment.sender_account,
        receiver_account=payment.receiver_account,
        amount=payment.amount,
        memo=payment.memo,
        status="pending"
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    try:
        # Forward payment to gateway
        gateway_response = gateway_client.submit_payment(
            sender_account=payment.sender_account,
            receiver_account=payment.receiver_account,
            amount=payment.amount,
            memo=payment.memo
        )
        
        # Update database record with confirmation_id from gateway
        db_payment.confirmation_id = gateway_response.get("confirmation_id")
        db_payment.status = gateway_response.get("status", "pending")
        db.commit()
        db.refresh(db_payment)
        
    except httpx.HTTPError as e:
        # If gateway call fails, keep the payment in DB with pending status
        # This allows for retry later
        pass
    
    return PaymentResponse.model_validate(db_payment)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: str, db: Session = Depends(get_db)):
    """
    Get payment status.
    
    - Retrieve payment from your database
    - Poll the gateway for updated status
    - Update local status if changed
    - Return the current payment status
    """
    # Query database for payment by internal ID
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not db_payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with id {payment_id} not found"
        )
    
    # Poll gateway for all statuses if we have a confirmation_id
    if db_payment.confirmation_id:
        try:
            gateway_statuses = gateway_client.get_all_statuses()
            
            # Find matching payment by confirmation_id and update local status
            for gateway_status in gateway_statuses:
                if gateway_status.get("confirmation_id") == db_payment.confirmation_id:
                    new_status = gateway_status.get("status")
                    if new_status and new_status != db_payment.status:
                        db_payment.status = new_status
                        # Update updated_at timestamp
                        db_payment.updated_at = datetime.utcnow()
                        db.commit()
                        db.refresh(db_payment)
                    break
                    
        except httpx.HTTPError:
            # If gateway call fails, return current database status
            pass
    
    return PaymentResponse.model_validate(db_payment)
