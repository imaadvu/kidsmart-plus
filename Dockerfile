FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --upgrade pip

# Copy all requirement files
COPY requirements*.txt /app/

# Install base dependencies first (smaller, faster)
RUN pip install --timeout=1000 --retries=5 -r /app/requirements-base.txt

# Install ML/data science packages (large but usually cached well)
RUN pip install --timeout=1000 --retries=5 -r /app/requirements-ml.txt

# Install playwright last (largest package, most likely to timeout)
RUN pip install --timeout=1000 --retries=5 -r /app/requirements-playwright.txt

COPY . /app

EXPOSE 8000 8501

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

