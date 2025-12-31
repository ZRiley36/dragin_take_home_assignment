"""
HTTP client for interacting with the external payment gateway.
"""
import httpx
from typing import Dict, List, Optional
from datetime import datetime


GATEWAY_BASE_URL = "http://localhost:8001"
GATEWAY_TIMEOUT = 30.0


class GatewayClient:
    """Client for interacting with the payment gateway API."""

    def __init__(self, base_url: str = GATEWAY_BASE_URL, timeout: float = GATEWAY_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout

    def submit_payment(
        self,
        sender_account: str,
        receiver_account: str,
        amount: float,
        memo: Optional[str] = None
    ) -> Dict:
        """
        Submit a payment to the gateway.

        Args:
            sender_account: Sender's account number
            receiver_account: Receiver's account number
            amount: Payment amount
            memo: Optional payment memo

        Returns:
            Dictionary with confirmation_id, status, and created_at

        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.base_url}/submit"
        payload = {
            "sender_account": sender_account,
            "receiver_account": receiver_account,
            "amount": amount,
        }
        if memo:
            payload["memo"] = memo

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    def get_all_statuses(self) -> List[Dict]:
        """
        Get the status of all payments from the gateway.

        Returns:
            List of dictionaries with confirmation_id, status, created_at, and updated_at

        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.base_url}/status"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json()


# Singleton instance
gateway_client = GatewayClient()

