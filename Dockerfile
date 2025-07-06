FROM python:3.13-slim

WORKDIR /bot

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "-u", "main.py"]