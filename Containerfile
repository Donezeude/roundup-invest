FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY roundup/ roundup/

ENV LEDGER_PATH=/data/ledger.json
ENV TX_CSV_PATH=/data/transactions.csv
VOLUME /data

CMD ["uv", "run", "python", "-m", "roundup.main"]