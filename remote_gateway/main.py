from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import PaymentSubmission, PaymentResponse, StatusResponse
from .storage import storage

app = FastAPI(
    title="Payment Gateway (Mock)",
    description="A mock external payment gateway for testing purposes",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/submit", response_model=PaymentResponse)
def submit_payment(submission: PaymentSubmission):
    """
    Submit a new payment for processing.

    Returns a confirmation_id that can be used to track the payment status.
    The payment will initially be in 'pending' status.
    """
    record = storage.submit(submission)
    return PaymentResponse(
        confirmation_id=record.confirmation_id,
        status=record.status,
        created_at=record.created_at,
    )


@app.get("/status", response_model=list[StatusResponse])
def get_all_payment_statuses():
    """
    Get the status of all payments.

    Returns a list of all payments with their current status.
    The payment status is determined by the receiver's account number:
    - Last digit 0-3: settled
    - Last digit 4-6: returned
    - Last digit 7-9: failed

    Status remains 'pending' until PAYMENT_DELAY_SECONDS has elapsed (default: 10s).
    """
    records = storage.get_all_statuses()
    return [
        StatusResponse(
            confirmation_id=record.confirmation_id,
            status=record.status,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
        for record in records
    ]
