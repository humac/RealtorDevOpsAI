FROM python:3.11-slim

WORKDIR /app

# System dependencies for WeasyPrint and PostGIS
# Retry apt-get update to handle transient network failures
RUN for i in 1 2 3; do \
      apt-get update -qq && break || sleep 5; \
    done && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgdal-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
