FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    USER_AGENT=query-planning-decomposition/0.1 \
    OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    OLLAMA_CHAT_MODEL=llama3.2:3b \
    OLLAMA_EMBED_MODEL=bge-m3:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY configs ./configs
COPY src ./src
COPY templates ./templates
COPY static ./static
COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
