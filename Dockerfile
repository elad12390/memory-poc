FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml /app

RUN pip install uv
RUN uv sync

COPY . /app

WORKDIR /app
CMD ["uv", "run", "src/main.py"]