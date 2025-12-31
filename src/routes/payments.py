"""
Payment Routes

TODO: Implement the payment endpoints here.

Required endpoints:
1. POST /payments - Submit a new payment
   - Accept payment details from the user
   - Store the payment in your database
   - Forward the payment to the remote gateway
   - Return the payment with its initial status

2. GET /payments/{payment_id} - Get payment status
   - Retrieve payment from your database
   - Optionally poll the gateway for updated status
   - Return the current payment status

Bonus endpoints:
3. GET /payments - List all payments (with optional filters)
"""

from fastapi import APIRouter

router = APIRouter()


# TODO: Implement your endpoints
#
# @router.post("/")
# def create_payment(...):
#     pass
#
# @router.get("/{payment_id}")
# def get_payment(payment_id: str, ...):
#     pass
