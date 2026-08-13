FROM python:3.13.14-alpine3.23

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./

RUN pip install --upgrade pip \
    && pip install .

CMD ["python", "-m", "main"]