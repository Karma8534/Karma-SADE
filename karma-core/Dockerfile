FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only PyTorch first (much smaller than full CUDA torch)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Then install everything else
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose chat server port
EXPOSE 8340

# Default: run chat server
CMD ["python", "-u", "server.py"]
