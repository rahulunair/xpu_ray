FROM python:3.9-slim

RUN pip install fastapi uvicorn

COPY auth.py /app/auth.py
WORKDIR /app

CMD ["uvicorn", "auth:app", "--host", "0.0.0.0", "--port", "8001"]