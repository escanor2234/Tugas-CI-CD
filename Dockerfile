FROM ghcr.io/astral-sh/uv:0.10.8 AS uv
FROM python:3.12-slim

COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project

COPY src/ src/
ENV OUTPUT_CSV=/app/data/data_saham_2menit.csv

ENTRYPOINT ["/app/.venv/bin/python", "-m", "src.main"]
