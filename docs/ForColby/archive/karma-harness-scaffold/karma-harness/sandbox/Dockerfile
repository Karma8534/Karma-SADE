FROM python:3.12-slim

WORKDIR /workspace

# Install execution tools
RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    bash \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

# Install sandbox server deps
RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn==0.30.6 \
    aiofiles==24.1.0

COPY scripts/server.py /server.py

EXPOSE 8888

CMD ["python", "/server.py"]
