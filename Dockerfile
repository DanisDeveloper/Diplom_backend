FROM python:3.12.8

WORKDIR /diplom

COPY ./app ./app

COPY ./requirements.txt .

COPY ./.env .

COPY ./public ./public

RUN pip install --upgrade pip &&  pip install --no-cache-dir -r requirements.txt


EXPOSE 8000

# Не работает, потому что не может достучаться до postgresql
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
