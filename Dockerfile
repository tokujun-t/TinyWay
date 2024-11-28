FROM python:3-alpine AS tinyway
LABEL authors="iktahana"

COPY requirements.txt .
RUN pip install gunicorn
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
WORKDIR /app

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]