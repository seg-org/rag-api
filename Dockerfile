FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 3000

WORKDIR /app/app

CMD ["python", "main.py"]
