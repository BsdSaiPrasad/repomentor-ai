FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY docs ./docs
COPY sample_repos ./sample_repos
COPY scripts ./scripts

COPY deploy/gcp/backend-start.sh /app/backend-start.sh
RUN chmod +x /app/backend-start.sh
ENV RAG_PROVIDER=vertex
ENV GOOGLE_CLOUD_LOCATION=us-central1

EXPOSE 8080

CMD ["/app/backend-start.sh"]
