# Payment Tracking System

Build a payment tracking service that integrates with an external payment gateway.

Consider that there is an API provider for payments that Dragin is integrated to. The API provider allows you to submit payments initiated by Dragin, and also allows you to get the status of all payments ever submitted by Dragin. The user of your system only interacts with Dragin, and cannot directly query the API provider. Your task is to design a system that allows users to both submit payments and get the status of those payments tracked by Dragin.

## Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Make
  - Linux: `sudo apt install make`
  - macOS: `brew install make`

### Getting Started

```bash
# Start infrastructure (gateway + database)
make up

# Install dependencies in a virtual environment
make install

# Run the app
make run-app
```

This starts:
- Payment gateway at `http://localhost:8001`
- PostgreSQL database at `localhost:5432`
- Your app at `http://localhost:8000` (with hot-reload)

Alternatively, you can set up manually:

```bash
# Start infrastructure
make up

# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
uvicorn src.main:app --reload --port 8000
```

## Your Task

Build a FastAPI application that allows users to submit payments and track their status. Your service should:

1. Accept payment submissions from users
2. Store payments in the database
3. Forward payments to the remote gateway
4. Track payment lifecycle by polling the gateway
5. Expose your own status endpoint (not just proxy the gateway)

### Required Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payments` | Submit a new payment |
| GET | `/payments/{id}` | Get payment status |

### Syncing Status from Gateway

Your local database won't automatically know when a payment status changes on the gateway. Consider how you'll keep your data in sync:

- **On-demand**: Fetch from gateway when a user requests status
- **Background sync**: A separate script that periodically polls the gateway and updates your database


## What's Provided

- **Database connection** is already configured in `src/database.py`
- **Tables are auto-created** on app startup via `init_db()`
- You just need to define your SQLAlchemy models in `src/models.py`

Example model structure:
```python
from sqlalchemy import Column, String, Float, DateTime
from .database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True)
    # TODO: Add your columns
```

## Remote Gateway API
Remember, the Gateway API is an external API that only Dragin is connected to. Users of our system do not have access to this. Hence, you should not modify the functionality of this server and should instead build your system of tracking payments around this.

The mock payment gateway runs at `http://localhost:8001` and provides:

### POST /submit

Submit a payment for processing.

**Request:**
```json
{
  "sender_account": "123456789",
  "receiver_account": "987654321",
  "amount": 100.50,
  "memo": "Optional memo"
}
```

**Response:**
```json
{
  "confirmation_id": "uuid-string",
  "status": "pending",
  "created_at": "2024-01-01T12:00:00Z"
}
```

The Gateway server returns a `confirmation_id` will uniquely identify transactions.

### GET /status

Get status of all payments.

**Response:**
```json
[
  {
    "confirmation_id": "uuid-string",
    "status": "settled",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:10Z"
  },
  {
    "confirmation_id": "uuid-string-2",
    "status": "pending",
    "created_at": "2024-01-01T12:00:05Z",
    "updated_at": "2024-01-01T12:00:05Z"
  }
]
```

### Status Behavior

- Payments start as `pending`
- After ~60 seconds, status resolves based on the **receiver's account number**:
  - Last digit 0-3: `settled`
  - Last digit 4-6: `returned`
  - Last digit 7-9: `failed`

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make up` | Start infrastructure (gateway, database) |
| `make down` | Stop infrastructure |
| `make logs` | View container logs |
| `make install` | Create venv and install dependencies |
| `make run-app` | Run the app locally |
| `make clean` | Remove containers, volumes, venv, and cache |

## Project Structure

```
payments_proj/
├── remote_gateway/          # DO NOT MODIFY - Mock payment gateway
├── src/                     # YOUR CODE GOES HERE
│   ├── main.py              # FastAPI app entry point (configured)
│   ├── models.py            # TODO: Define your models here
│   ├── database.py          # Database connection (configured)
│   └── routes/
│       └── payments.py      # TODO: Implement endpoints
├── requirements.txt
├── docker-compose.yml
└── Makefile
```
## Final Submission

- A working application that lets users submit payments, and a system that allows users to get the most up-to-date status of payments.
- For the final version you're proud of, package all your code in a zip file.

---

Thank you for taking the time to work on this project. We know your time is valuable, and we genuinely appreciate the effort you're putting in. This problem reflects the kind of challenges we tackle daily, and we hope you find it engaging. Good luck!
