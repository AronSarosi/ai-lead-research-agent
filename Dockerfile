# Production image for the AI Lead Research Agent (Streamlit) on Google Cloud Run.
#
# Cloud Run gives the container a $PORT env var (default 8080) and expects the
# app to listen on 0.0.0.0. Platform terminates HTTPS; the app speaks plain HTTP.
#
# Python 3.12 is chosen as a stable base with broad wheel availability for the
# pinned deps (langgraph, langchain, pandas, pydantic). The project requires
# Python 3.10+ per its README, so 3.12 is comfortably within range.

FROM python:3.12-slim

# - PYTHONDONTWRITEBYTECODE: no .pyc files cluttering the image
# - PYTHONUNBUFFERED: logs stream straight to Cloud Run (no buffering)
# - PORT: sensible default; Cloud Run overrides this at runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080

WORKDIR /app

# Install dependencies first, in their own layer, so this expensive step is
# cached and only re-runs when requirements.txt actually changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the application code.
COPY . .

# Run as a non-root user (Cloud Run best practice; limits blast radius).
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Document the default port (Cloud Run ignores EXPOSE but it aids local use).
EXPOSE 8080

# Streamlit must bind 0.0.0.0 and the Cloud Run $PORT, run headless, and have
# CORS/XSRF protections off (the platform fronts HTTPS and the websocket).
# Use shell form so $PORT is expanded at container start.
CMD streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
