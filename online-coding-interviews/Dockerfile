# Multi-stage build: Backend (Python) + Frontend (Static Files)
# Stage 1: Build backend and prepare application
FROM python:3.9-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image with everything
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy entire application
COPY . .

# Create directory for database
RUN mkdir -p /app/backend/instance

# Expose ports
# 5000: Flask backend with SocketIO
# 8080: Static frontend files
EXPOSE 5000 8080

# Set environment variables
ENV FLASK_APP=backend/app.py
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start both backend and frontend
CMD ["sh", "-c", "cd backend && python app.py & cd frontend && python -m http.server 8080 --bind 0.0.0.0"]
