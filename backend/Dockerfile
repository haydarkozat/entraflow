FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY seed ./seed

EXPOSE 8000

# Standardmäßig gegen den mitgelieferten Graph-Mock (kein echter Tenant nötig).
ENV GRAPH_MODE=memory

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
