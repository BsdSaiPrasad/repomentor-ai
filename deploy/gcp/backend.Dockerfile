FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY docs ./docs
COPY scripts ./scripts

COPY deploy/gcp/backend-start.sh /app/backend-start.sh
RUN chmod +x /app/backend-start.sh
RUN python /app/scripts/ingest_syllabus.py

EXPOSE 8080

CMD ["/app/backend-start.sh"]
