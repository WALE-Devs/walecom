# ================================================
# Stage 1: Base image with shared setup
# ================================================
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Common system dependencies (for psycopg2, Pillow, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# ================================================
# Stage 2: Development (with tools & hot reload)
# ================================================
FROM base AS development

# Install dev dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY src/ .

# Expose Django port
EXPOSE 8000

# Default command for development
# (will run migrations + Django dev server)
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

# ================================================
# Stage 3: Builder (compile dependencies for prod)
# ================================================
FROM base AS builder

RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ================================================
# Stage 4: Production (minimal image)
# ================================================
FROM python:3.12-slim AS production

WORKDIR /app

# Copy only necessary runtime libs from builder
COPY --from=builder /install /usr/local

# Copy app source
COPY src/ .

# Expose Django port
EXPOSE 8000

# Environment variables
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV PORT=8000

# Command for production
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3"]
