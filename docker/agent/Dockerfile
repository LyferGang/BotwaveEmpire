# Botwave Agent Docker Image
# Multi-stage build for optimized production image

FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim as production

# Security: Run as non-root user
RUN groupadd -r botwave && useradd -r -g botwave botwave

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create required directories
RUN mkdir -p /app/data /app/logs /app/vault && \
    chown -R botwave:botwave /app

# Switch to non-root user
USER botwave

# Environment configuration
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from agents.business_agent import BusinessAgent; a = BusinessAgent(); print(a.health_check())" || exit 1

# Default command
CMD ["python", "-m", "agents.business_agent"]
