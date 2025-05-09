FROM python:3.12.8-slim

WORKDIR /backend

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini .

# Create public directory (will be overridden by volume mount)
RUN mkdir -p /backend/public

EXPOSE 8000

#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["sh", "-c", "alembic upgrade head && python -m app.main"]
