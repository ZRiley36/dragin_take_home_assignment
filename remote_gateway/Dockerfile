FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn[standard]

COPY . /app/remote_gateway

ENV PYTHONPATH=/app
ENV PAYMENT_DELAY_SECONDS=60

EXPOSE 8001

CMD ["uvicorn", "remote_gateway.main:app", "--host", "0.0.0.0", "--port", "8001"]
