# BASE
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# BUILDER
FROM base AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \ 
    libreoffice


ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry install --without dev

COPY . /app

# RUNNER
FROM base AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq5

ENV PATH="/app/.venv/bin:$PATH"
COPY --from=builder /app /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]