FROM python:3.12-slim


RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir \
    fastapi==0.68.0 \
    uvicorn==0.15.0 \
    python-multipart \
    python-jose[cryptography]


RUN useradd -m -u 1000 authuser
COPY auth.py /app/auth.py

WORKDIR /app
RUN chown -R authuser:authuser /app
USER authuser
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:9001/auth/health || exit 1


EXPOSE 9001
CMD ["uvicorn", "auth:app", "--host", "0.0.0.0", "--port", "9001"]