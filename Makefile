.PHONY: up down logs run-app install clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  make up        - Start infrastructure (gateway, database)"
	@echo "  make down      - Stop infrastructure"
	@echo "  make logs      - View container logs"
	@echo "  make install   - Create venv and install dependencies"
	@echo "  make run-app   - Run the app locally (requires make install first)"
	@echo "  make clean     - Remove containers, volumes, venv, and cache"

# Start infrastructure (gateway + database)
up:
	docker-compose up -d
	@echo "Infrastructure starting..."
	@echo "  - Gateway: http://localhost:8001"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "Use 'make logs' to view logs"

# Stop infrastructure
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Create venv and install dependencies
install:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

# Run the app locally
run-app:
	./venv/bin/uvicorn src.main:app --reload --port 8000

# Clean up
clean:
	docker-compose down -v --remove-orphans
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
