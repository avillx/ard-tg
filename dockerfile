FROM python:3.13.14-alpine3.23

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
COPY README.md ./

RUN pip install --upgrade pip \
    && pip install .

# Исходники
COPY src/ ./src/

CMD ["python", "-m", "src.main"]