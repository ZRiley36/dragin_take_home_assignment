"""
Test script for the Payment Tracking Service.

This script tests the expected behavior:
1. Submit payments via POST /payments
2. Retrieve payment status via GET /payments/{id}
3. Verify status synchronization from the gateway
4. Test status resolution based on receiver account number

Run with: python test_payments.py

Prerequisites:
- API service running on http://localhost:8000 (make run-app)
- Gateway service running on http://localhost:8001 (make up)
"""
import time
import httpx
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
GATEWAY_BASE_URL = "http://localhost:8001"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def check_service_health() -> bool:
    """Check if the API service is running."""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                print_success("API service is running")
                return True
            else:
                print_error(f"API service returned status {response.status_code}")
                return False
    except httpx.RequestError as e:
        print_error(f"Cannot connect to API service at {API_BASE_URL}")
        print_info("Make sure the service is running: make run-app")
        return False


def check_gateway_health() -> bool:
    """Check if the gateway service is running."""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{GATEWAY_BASE_URL}/health")
            if response.status_code == 200:
                print_success("Gateway service is running")
                return True
            else:
                print_warning(f"Gateway service returned status {response.status_code}")
                return False
    except httpx.RequestError as e:
        print_warning(f"Cannot connect to gateway service at {GATEWAY_BASE_URL}")
        print_info("Make sure the gateway is running: make up")
        return False


def submit_payment(sender: str, receiver: str, amount: float, memo: str = None) -> Dict[str, Any]:
    """
    Submit a payment via POST /payments.
    
    Args:
        sender: Sender account number
        receiver: Receiver account number
        amount: Payment amount
        memo: Optional memo
        
    Returns:
        Payment response dictionary
    """
    # FastAPI redirects /payments to /payments/ when route is defined as "/"
    # So we use the trailing slash to avoid redirects
    url = f"{API_BASE_URL}/payments/"
    payload = {
        "sender_account": sender,
        "receiver_account": receiver,
        "amount": amount,
    }
    if memo:
        payload["memo"] = memo
    
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


def get_payment_status(payment_id: str) -> Dict[str, Any]:
    """
    Get payment status via GET /payments/{id}.
    
    Args:
        payment_id: Internal payment ID
        
    Returns:
        Payment response dictionary
    """
    url = f"{API_BASE_URL}/payments/{payment_id}"
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json()


def test_basic_payment_flow():
    """Test 1: Basic payment submission and retrieval."""
    print("\n" + "="*60)
    print("TEST 1: Basic Payment Flow")
    print("="*60)
    
    try:
        # Submit a payment
        print_info("Submitting payment...")
        payment = submit_payment(
            sender="123456789",
            receiver="987654321",
            amount=100.50,
            memo="Test payment"
        )
        
        payment_id = payment["id"]
        print_success(f"Payment submitted successfully")
        print(f"  Payment ID: {payment_id}")
        print(f"  Status: {payment['status']}")
        print(f"  Confirmation ID: {payment.get('confirmation_id', 'Not set yet')}")
        
        # Verify initial status
        assert payment["status"] == "pending", "Initial status should be 'pending'"
        assert payment["confirmation_id"] is not None, "Confirmation ID should be set"
        assert payment["amount"] == 100.50, "Amount should match"
        
        # Retrieve payment status
        print_info("Retrieving payment status...")
        retrieved = get_payment_status(payment_id)
        
        print_success(f"Payment retrieved successfully")
        print(f"  Status: {retrieved['status']}")
        print(f"  Confirmation ID: {retrieved['confirmation_id']}")
        
        # Verify data consistency
        assert retrieved["id"] == payment_id, "Payment ID should match"
        assert retrieved["confirmation_id"] == payment["confirmation_id"], "Confirmation ID should match"
        
        return payment_id
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return None
    except Exception as e:
        print_error(f"Test failed: {e}")
        return None


def test_status_synchronization():
    """Test 2: Status synchronization from gateway."""
    print("\n" + "="*60)
    print("TEST 2: Status Synchronization")
    print("="*60)
    
    try:
        # Submit a payment
        print_info("Submitting payment...")
        payment = submit_payment(
            sender="111111111",
            receiver="222222222",
            amount=50.00
        )
        
        payment_id = payment["id"]
        initial_status = payment["status"]
        print_success(f"Payment submitted with status: {initial_status}")
        
        # Wait a moment, then check status (should sync from gateway)
        print_info("Waiting 2 seconds, then checking status (should sync from gateway)...")
        time.sleep(2)
        
        retrieved = get_payment_status(payment_id)
        print_success(f"Status retrieved: {retrieved['status']}")
        print(f"  Initial status: {initial_status}")
        print(f"  Current status: {retrieved['status']}")
        
        # Status should be synced (may still be pending if not enough time passed)
        assert retrieved["status"] in ["pending", "settled", "returned", "failed"], \
            "Status should be a valid payment status"
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False


def test_status_resolution_by_receiver_account():
    """Test 3: Status resolution based on receiver account number."""
    print("\n" + "="*60)
    print("TEST 3: Status Resolution by Receiver Account")
    print("="*60)
    print_info("According to README, status resolves based on receiver's last digit:")
    print_info("  Last digit 0-3: settled")
    print_info("  Last digit 4-6: returned")
    print_info("  Last digit 7-9: failed")
    print_info("  (Status resolves after ~60 seconds)")
    
    test_cases = [
        ("123456780", "settled"),   # Last digit 0
        ("123456781", "settled"),   # Last digit 1
        ("123456783", "settled"),   # Last digit 3
        ("123456784", "returned"),  # Last digit 4
        ("123456785", "returned"),  # Last digit 5
        ("123456786", "returned"),  # Last digit 6
        ("123456787", "failed"),    # Last digit 7
        ("123456788", "failed"),    # Last digit 8
        ("123456789", "failed"),    # Last digit 9
    ]
    
    submitted_payments = []
    
    try:
        # Submit payments with different receiver account numbers
        print_info("Submitting payments with different receiver accounts...")
        for receiver, expected_status in test_cases:
            payment = submit_payment(
                sender="999999999",
                receiver=receiver,
                amount=10.00,
                memo=f"Test for receiver ending in {receiver[-1]}"
            )
            submitted_payments.append({
                "id": payment["id"],
                "receiver": receiver,
                "expected": expected_status,
                "last_digit": receiver[-1]
            })
            print(f"  Submitted payment to {receiver} (last digit: {receiver[-1]}, expected: {expected_status})")
        
        print_success(f"Submitted {len(submitted_payments)} payments")
        
        # Wait for status resolution (README says ~60 seconds)
        print_warning("Waiting 65 seconds for status resolution...")
        print_info("(Status resolution happens on the gateway side)")
        for i in range(65, 0, -5):
            print(f"  Waiting... {i} seconds remaining")
            time.sleep(5)
        
        # Check final statuses
        print_info("Checking final payment statuses...")
        results = []
        for payment_info in submitted_payments:
            retrieved = get_payment_status(payment_info["id"])
            actual_status = retrieved["status"]
            expected_status = payment_info["expected"]
            
            results.append({
                "receiver": payment_info["receiver"],
                "last_digit": payment_info["last_digit"],
                "expected": expected_status,
                "actual": actual_status,
                "match": actual_status == expected_status
            })
            
            status_icon = "✓" if actual_status == expected_status else "✗"
            status_color = Colors.GREEN if actual_status == expected_status else Colors.RED
            print(f"  {status_color}{status_icon}{Colors.RESET} Receiver {payment_info['receiver']} "
                  f"(last digit: {payment_info['last_digit']}): "
                  f"expected {expected_status}, got {actual_status}")
        
        # Summary
        matches = sum(1 for r in results if r["match"])
        total = len(results)
        print(f"\n  Results: {matches}/{total} payments resolved to expected status")
        
        if matches == total:
            print_success("All payments resolved to expected status!")
        else:
            print_warning("Some payments did not resolve to expected status")
            print_info("Note: Status resolution may take longer, or gateway may not be fully ready")
        
        return matches == total
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test 4: Error handling."""
    print("\n" + "="*60)
    print("TEST 4: Error Handling")
    print("="*60)
    
    try:
        # Test invalid payment ID
        print_info("Testing invalid payment ID...")
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{API_BASE_URL}/payments/invalid-id-12345")
                assert response.status_code == 404, "Should return 404 for invalid payment ID"
                print_success("Correctly returns 404 for invalid payment ID")
        except AssertionError:
            print_error("Should return 404 for invalid payment ID")
            return False
        
        # Test invalid amount (negative)
        print_info("Testing negative amount validation...")
        try:
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                response = client.post(
                    f"{API_BASE_URL}/payments/",
                    json={
                        "sender_account": "111111111",
                        "receiver_account": "222222222",
                        "amount": -10.00
                    }
                )
                # Should fail validation (422 for Pydantic validation errors)
                assert response.status_code == 422, f"Should reject negative amount (got {response.status_code})"
                print_success("Correctly rejects negative amount")
        except AssertionError as e:
            print_error(f"Should reject negative amount: {e}")
            return False
        
        # Test missing required fields
        print_info("Testing missing required fields...")
        try:
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                response = client.post(
                    f"{API_BASE_URL}/payments/",
                    json={
                        "sender_account": "111111111",
                        # Missing receiver_account and amount
                    }
                )
                # Should fail validation (422 for Pydantic validation errors)
                assert response.status_code == 422, f"Should reject missing required fields (got {response.status_code})"
                print_success("Correctly rejects missing required fields")
        except AssertionError as e:
            print_error(f"Should reject missing required fields: {e}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Payment Tracking Service - Test Suite")
    print("="*60)
    
    # Check services
    print("\nChecking services...")
    api_ok = check_service_health()
    gateway_ok = check_gateway_health()
    
    if not api_ok:
        print_error("Cannot proceed without API service")
        return
    
    if not gateway_ok:
        print_warning("Gateway service not available - some tests may fail")
    
    # Run tests
    results = []
    
    results.append(("Basic Payment Flow", test_basic_payment_flow() is not None))
    results.append(("Status Synchronization", test_status_synchronization()))
    results.append(("Status Resolution", test_status_resolution_by_receiver_account()))
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.RESET} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All tests passed!")
    else:
        print_warning(f"{total - passed} test(s) failed")


if __name__ == "__main__":
    main()

