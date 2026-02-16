FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg2-binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose chat server port
EXPOSE 8340

# Default: run chat server (use docker run ... python bootstrap.py for one-off bootstrap)
CMD ["python", "-u", "server.py"]
