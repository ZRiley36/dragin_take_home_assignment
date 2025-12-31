import os
import uuid
from datetime import datetime
from typing import Dict

from .models import PaymentStatus, PaymentSubmission


class PaymentRecord:
    def __init__(self, submission: PaymentSubmission):
        self.confirmation_id = str(uuid.uuid4())
        self.sender_account = submission.sender_account
        self.receiver_account = submission.receiver_account
        self.amount = submission.amount
        self.memo = submission.memo
        self.status = PaymentStatus.PENDING
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at

    def get_final_status(self) -> PaymentStatus:
        """Determine final status based on last digit of receiver account."""
        last_digit = int(self.receiver_account[-1]) if self.receiver_account[-1].isdigit() else 0

        if last_digit <= 3:
            return PaymentStatus.SETTLED
        elif last_digit <= 6:
            return PaymentStatus.RETURNED
        else:
            return PaymentStatus.FAILED

    def should_resolve(self, delay_seconds: int) -> bool:
        """Check if enough time has passed to resolve the payment."""
        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return elapsed >= delay_seconds


class InMemoryStorage:
    def __init__(self):
        self.payments: Dict[str, PaymentRecord] = {}
        self.delay_seconds = int(os.getenv("PAYMENT_DELAY_SECONDS", "10"))

    def submit(self, submission: PaymentSubmission) -> PaymentRecord:
        """Submit a new payment and return the record."""
        record = PaymentRecord(submission)
        self.payments[record.confirmation_id] = record
        return record

    def get_all_statuses(self) -> list[PaymentRecord]:
        """Get all payments, resolving any that have passed the delay."""
        for record in self.payments.values():
            if record.status == PaymentStatus.PENDING and record.should_resolve(self.delay_seconds):
                record.status = record.get_final_status()
                record.updated_at = datetime.utcnow()

        return list(self.payments.values())


storage = InMemoryStorage()
