FROM python:3.13-slim AS base

RUN addgroup --system app && adduser --system --group app

WORKDIR /app


FROM base AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .

RUN pip install -r requirements.txt


FROM base AS final

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY ./src/app /app

USER app

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
