FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -U --no-cache-dir -r requirements.txt

COPY rag.py .
COPY .env .

CMD ["python", "rag.py"]

