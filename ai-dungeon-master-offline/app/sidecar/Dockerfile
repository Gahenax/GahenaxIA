FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy requirements file first to utilize Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH environment variable so python can import from the sidecar module root
ENV PYTHONPATH=/app/sidecar/python

# Run FastAPI app
WORKDIR /app/sidecar/python
CMD ["python", "main.py"]
