FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY requirements-dev.txt ./requirements-dev.txt
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY . .

CMD ["python", "-m", "pytest", "-q"]
