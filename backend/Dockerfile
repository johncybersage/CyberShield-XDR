# =============================================================================
# CyberShield XDR — Backend Dockerfile
# Multi-stage build: builder installs deps, final image is minimal.
# Runs as non-root user for security.
# =============================================================================

# --- Stage 1: Dependency Builder ---
FROM python:3.12-slim AS builder

WORKDIR /build

# Install system dependencies for compiled packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libmagic1 \
    nmap \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Production Image ---
FROM python:3.12-slim AS production

# Security: run as non-root
RUN groupadd -r cybershield && useradd -r -g cybershield -d /app -s /sbin/nologin cybershield

# Install runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libmagic1 \
    nmap \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy application code
COPY --chown=cybershield:cybershield . .

# Create required directories
RUN mkdir -p /app/uploads /app/reports /app/logs && \
    chown -R cybershield:cybershield /app/uploads /app/reports /app/logs

USER cybershield

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "backend.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
