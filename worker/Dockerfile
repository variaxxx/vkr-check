# BASE
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# BUILDER
FROM base AS builder

RUN apt-get update && apt-get install -y \
  build-essential \
  libgl1 \
  libglib2.0-0 \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry install --without dev --no-root

COPY . /app

# RUNNER
FROM base AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y \
  libpq5 \
  libgl1 \
  libglib2.0-0 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libcairo2 \
  libgdk-pixbuf-2.0-0 \
  poppler-utils \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
  
ENV PATH="/app/.venv/bin:$PATH" \
  OPENCV_IO_ENABLE_OPENEXR=0

CMD ["celery", "-A", "src.main", "worker", "--loglevel=info"]