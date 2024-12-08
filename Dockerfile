FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/app

ADD src /app

RUN pip install --no-cache-dir -r /app/requirements.txt

ENV FLASK_APP=/app/app
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0", "--debug"]
